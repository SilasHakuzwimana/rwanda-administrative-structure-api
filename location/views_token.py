from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
import secrets
import hashlib
import re

from .models import APICustomer, APIKey, AllowedOrigin
from .serializers import APICustomerSerializer, APIKeySerializer


# ============================================
# Token Generation Functions
# ============================================

def generate_api_key(customer, name, plan=None):
    """Generate a new API key for a customer"""
    if not plan:
        plan = customer.plan
    
    # Generate a unique key
    key_prefix = secrets.token_hex(16)[:8]
    key = f"rw_admin_api_{plan}_{key_prefix}"
    
    # Create the API key
    api_key = APIKey.objects.create(
        customer=customer,
        name=name,
        key=key,
        key_prefix=key_prefix,
        is_active=True
    )
    
    # Invalidate cache
    cache.delete_pattern(f'apikey_*')
    cache.delete_pattern(f'customer_*')
    
    return api_key


def validate_origin(origin, customer):
    """Validate if origin is allowed for the customer"""
    # Allow localhost and development origins
    allowed_origins = ['localhost', '127.0.0.1', '0.0.0.0']
    
    # Check if origin is in allowed list
    for allowed in allowed_origins:
        if allowed in origin:
            return True
    
    # Check if origin is configured for the customer
    allowed_origins = AllowedOrigin.objects.filter(
        customer=customer,
        is_active=True
    )
    
    for allowed in allowed_origins:
        if allowed.origin in origin or origin in allowed.origin:
            return True
    
    return False


# ============================================
# API Views
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_customer(request):
    """
    Register a new customer and generate API key
    """
    try:
        email = request.data.get('email')
        name = request.data.get('name')
        plan = request.data.get('plan', 'free')
        origin = request.data.get('origin', '')
        
        # Validate input
        if not email or not name:
            return Response({
                'success': False,
                'error': 'Email and name are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if customer already exists
        if APICustomer.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'error': 'Customer with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create customer
        customer = APICustomer.objects.create(
            email=email,
            name=name,
            plan=plan,
            is_active=True
        )
        
        # Generate API key
        api_key = generate_api_key(customer, f"Default Key for {name}")
        
        # Add origin if provided
        if origin:
            AllowedOrigin.objects.create(
                customer=customer,
                origin=origin,
                is_active=True
            )
        
        # Invalidate cache
        cache.delete('customers_active')
        cache.delete(f'customer_email_{email.lower()}')
        
        return Response({
            'success': True,
            'message': 'Customer registered successfully',
            'data': {
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'plan': customer.plan,
                },
                'api_key': {
                    'key': api_key.key,
                    'prefix': api_key.key_prefix,
                    'name': api_key.name,
                },
                'allowed_origin': origin if origin else None,
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_token(request):
    """
    Generate a new API token for an existing customer
    """
    try:
        email = request.data.get('email')
        key_name = request.data.get('key_name', 'New API Key')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find customer
        try:
            customer = APICustomer.objects.get(email=email, is_active=True)
        except APICustomer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Customer not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate new API key
        api_key = generate_api_key(customer, key_name)
        
        return Response({
            'success': True,
            'message': 'API token generated successfully',
            'data': {
                'api_key': {
                    'key': api_key.key,
                    'prefix': api_key.key_prefix,
                    'name': api_key.name,
                    'created_at': api_key.created_at,
                },
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'plan': customer.plan,
                }
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def validate_token(request):
    """
    Validate an API token
    """
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({
                'success': False,
                'error': 'Invalid authorization header. Use: Bearer <token>'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.replace('Bearer ', '')
        
        # Find the API key
        try:
            api_key = APIKey.objects.get(key=token, is_active=True)
        except APIKey.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid or inactive API key'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Update last used
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])
        
        # Get customer
        customer = api_key.customer
        
        # Validate origin if provided
        origin = request.headers.get('Origin', '')
        if origin and not validate_origin(origin, customer):
            return Response({
                'success': False,
                'error': 'Origin not allowed'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'success': True,
            'message': 'Token is valid',
            'data': {
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'plan': customer.plan,
                },
                'api_key': {
                    'prefix': api_key.key_prefix,
                    'name': api_key.name,
                    'last_used': api_key.last_used_at,
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def revoke_token(request):
    """
    Revoke (deactivate) an API token
    """
    try:
        email = request.data.get('email')
        key_prefix = request.data.get('key_prefix')
        
        if not email or not key_prefix:
            return Response({
                'success': False,
                'error': 'Email and key_prefix are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find customer
        try:
            customer = APICustomer.objects.get(email=email)
        except APICustomer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Find and revoke the key
        try:
            api_key = APIKey.objects.get(
                customer=customer,
                key_prefix=key_prefix,
                is_active=True
            )
            api_key.is_active = False
            api_key.save()
        except APIKey.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Active API key not found with this prefix'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Invalidate cache
        cache.delete(f'apikey_{api_key.key}')
        cache.delete_pattern(f'apikey_prefix_{key_prefix}_*')
        
        return Response({
            'success': True,
            'message': f'API key {key_prefix} revoked successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_customer_keys(request, customer_id):
    """
    List all API keys for a customer
    """
    try:
        # Find customer
        try:
            customer = APICustomer.objects.get(id=customer_id)
        except APICustomer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all keys
        keys = APIKey.objects.filter(customer=customer).order_by('-created_at')
        
        return Response({
            'success': True,
            'data': {
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                },
                'keys': [
                    {
                        'prefix': key.key_prefix,
                        'name': key.name,
                        'is_active': key.is_active,
                        'created_at': key.created_at,
                        'last_used_at': key.last_used_at,
                    }
                    for key in keys
                ]
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)