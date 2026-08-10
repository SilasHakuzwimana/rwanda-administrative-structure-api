from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import stripe
from .models import APICustomer, APIKey, AllowedOrigin

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateSubscriptionView(APIView):
    """Create a new subscription via Stripe"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        email = request.user.email
        plan = request.data.get('plan', 'starter')
        
        # Create or get customer
        customer, created = APICustomer.objects.get_or_create(
            email=email,
            defaults={'name': request.user.get_full_name() or email}
        )
        
        if not customer.stripe_customer_id:
            stripe_customer = stripe.Customer.create(email=email)
            customer.stripe_customer_id = stripe_customer.id
            customer.save()
        
        # Price IDs (create these in Stripe dashboard)
        price_ids = {
            'starter': 'price_starter_monthly',
            'pro': 'price_pro_monthly',
            'enterprise': 'price_enterprise_monthly',
        }
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.stripe_customer_id,
            items=[{'price': price_ids.get(plan, price_ids['starter'])}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        
        customer.plan = plan
        customer.stripe_subscription_id = subscription.id
        customer.save()
        
        # Create initial API key
        api_key = APIKey.objects.create(
            customer=customer,
            name=f"Primary Key for {request.user.email}"
        )
        
        return Response({
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret,
            'api_key': api_key.key,
        })

class ManageAPIKeysView(APIView):
    """Manage API keys for authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        customer = APICustomer.objects.get(email=request.user.email)
        keys = customer.api_keys.all()
        return Response({
            'keys': [{
                'id': k.id,
                'name': k.name,
                'key_prefix': k.key_prefix,
                'created_at': k.created_at,
                'last_used_at': k.last_used_at,
            } for k in keys]
        })
    
    def post(self, request):
        customer = APICustomer.objects.get(email=request.user.email)
        name = request.data.get('name')
        
        if not name:
            return Response({'error': 'Key name required'}, status=400)
        
        key = APIKey.objects.create(customer=customer, name=name)
        return Response({
            'id': key.id,
            'key': key.key,  # Only shown once!
            'name': key.name,
            'message': 'Save this key now - it will not be shown again'
        })
    
    def delete(self, request, key_id):
        customer = APICustomer.objects.get(email=request.user.email)
        APIKey.objects.filter(id=key_id, customer=customer).delete()
        return Response({'message': 'Key revoked'})

class ManageOriginsView(APIView):
    """Manage allowed origins for API access"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        customer = APICustomer.objects.get(email=request.user.email)
        origins = customer.allowed_origins.all()
        return Response({
            'origins': [{'id': o.id, 'origin': o.origin} for o in origins],
            'plan_limit': self.get_origin_limit(customer.plan)
        })
    
    def post(self, request):
        customer = APICustomer.objects.get(email=request.user.email)
        origin = request.data.get('origin')
        
        # Check plan limit
        current_count = customer.allowed_origins.count()
        limit = self.get_origin_limit(customer.plan)
        
        if current_count >= limit:
            return Response({
                'error': f'Your plan allows only {limit} origins. Upgrade to add more.'
            }, status=403)
        
        allowed_origin, created = AllowedOrigin.objects.get_or_create(
            customer=customer,
            origin=origin
        )
        
        return Response({'message': f'Origin {origin} added'})
    
    def delete(self, request, origin_id):
        customer = APICustomer.objects.get(email=request.user.email)
        AllowedOrigin.objects.filter(id=origin_id, customer=customer).delete()
        return Response({'message': 'Origin removed'})
    
    def get_origin_limit(self, plan):
        limits = {'free': 1, 'starter': 3, 'pro': 10, 'enterprise': 999}
        return limits.get(plan, 1)