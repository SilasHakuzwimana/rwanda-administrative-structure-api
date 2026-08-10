from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.db.models import Sum  # ← Add this
from .models import APIKey, AllowedOrigin, APIUsage, APICustomer
from datetime import datetime, date
from django.utils import timezone


class APIAuthenticationMiddleware(MiddlewareMixin):
    """Authenticate API requests using API key"""
    
    def process_request(self, request):
        # Skip for admin and non-API paths
        if not request.path.startswith('/api/') or request.path.startswith('/api/auth'):
            return None
        
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return JsonResponse({
                'error': 'API key required. Include X-API-Key header.'
            }, status=401)
        
        # Validate API key
        try:
            api_key_obj = APIKey.objects.select_related('customer').get(
                key=api_key, 
                is_active=True,
                customer__is_active=True
            )
            request.api_customer = api_key_obj.customer
            request.api_key_obj = api_key_obj
            
            # Update last used timestamp
            api_key_obj.last_used_at = timezone.now()
            api_key_obj.save(update_fields=['last_used_at'])
            
        except APIKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid or inactive API key'}, status=401)
        
        return None
    
    def process_response(self, request, response):
        # Add rate limit headers to response
        if hasattr(request, 'api_customer'):
            response['X-RateLimit-Plan'] = request.api_customer.plan
            response['X-RateLimit-Remaining'] = str(self.get_remaining_requests(request.api_customer))
        return response
    
    def get_remaining_requests(self, customer):
        # Calculate remaining requests based on plan
        limits = {
            'free': 1000,
            'starter': 50000,
            'pro': 250000,
            'enterprise': 1000000,  # Essentially unlimited
        }
        
        today = date.today()
        used = APIUsage.objects.filter(
            customer=customer,
            date=today
        ).aggregate(total=Sum('request_count'))['total'] or 0  # ← Fixed!
        
        return limits.get(customer.plan, 1000) - used


class OriginRestrictionMiddleware(MiddlewareMixin):
    """Restrict API access to allowed origins per customer"""
    
    def process_request(self, request):
        if not hasattr(request, 'api_customer'):
            return None
        
        # Get origin from header
        origin = request.headers.get('Origin') or request.headers.get('Referer')
        
        if not origin:
            return JsonResponse({
                'error': 'Origin header required. Include Origin or Referer header.'
            }, status=400)
        
        # Handle multiple origins (comma-separated)
        origins = [o.strip() for o in origin.split(',')]
        
        # Check if ANY origin is allowed
        allowed = False
        for o in origins:
            if AllowedOrigin.objects.filter(
                customer=request.api_customer,
                origin=o,
                is_active=True
            ).exists():
                allowed = True
                break
        
        if not allowed:
            return JsonResponse({
                'error': f'Origin "{origin}" not allowed for this API key',
                'allowed_origins': list(request.api_customer.allowed_origins.values_list('origin', flat=True))
            }, status=403)
        
        return None

class UsageTrackingMiddleware(MiddlewareMixin):
    """Track API usage for billing"""
    
    def process_response(self, request, response):
        if hasattr(request, 'api_customer') and request.path.startswith('/api/'):
            # Skip tracking for OPTIONS requests
            if request.method == 'OPTIONS':
                return response
            
            # Track usage
            APIUsage.objects.create(
                customer=request.api_customer,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                origin=request.headers.get('Origin', 'unknown')
            )
        return response