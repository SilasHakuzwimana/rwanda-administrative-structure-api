from django.db import models
import secrets
import hashlib

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
class Province(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    # Add a unique constraint to ensure that the combination of name and country is unique
    class Meta:
        unique_together = ('name', 'country')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    # Add a unique constraint to ensure that the combination of name and province is unique
    # This will ensure that no two districts can have the same name within the same province
    class Meta:
        
        # Add a unique constraint to ensure that the combination of name and province is unique
        # This will ensure that no two districts can have the same name within the same province
        
        unique_together = ('name', 'province')
        #Optional: Add ordering to the model
        # This will ensure that the districts are ordered by name when queried
        # This is optional, but it can be useful for displaying the districts in a specific order
        ordering = ['name']
    def __str__(self):
        return self.name

class Sector(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'district')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):
        return self.name

class Cell(models.Model):
    name = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'sector')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):  
        return self.name
        

class Village(models.Model):
    name = models.CharField(max_length=100)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'cell')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):
        return self.name

# Customer API Customization

class APICustomer(models.Model):
    """Customer who subscribes to the API"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    plan = models.CharField(max_length=50, choices=[
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ], default='free')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.plan}"

class APIKey(models.Model):
    """API keys for customers (each customer can have multiple keys)"""
    customer = models.ForeignKey(APICustomer, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100, help_text="e.g., Production Key, Testing Key")
    key = models.CharField(max_length=64, unique=True, editable=False)
    key_prefix = models.CharField(max_length=8, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            # Generate a key like: wars_live_xxxxxxxxxxxx
            self.key_prefix = secrets.token_hex(16)[:8]
            self.key = f"wars_{self.plan}_{self.key_prefix}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer.name} - {self.name} ({self.key_prefix})"

class AllowedOrigin(models.Model):
    """Allowed origins (domains) for each customer"""
    customer = models.ForeignKey(APICustomer, on_delete=models.CASCADE, related_name='allowed_origins')
    origin = models.CharField(max_length=255, help_text="e.g., https://myapp.com or http://localhost:3000")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'origin']
    
    def __str__(self):
        return f"{self.customer.name} - {self.origin}"

class APIUsage(models.Model):
    """Track usage per customer for billing"""
    customer = models.ForeignKey(APICustomer, on_delete=models.CASCADE, related_name='api_usage')
    date = models.DateField(auto_now_add=True)
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    origin = models.CharField(max_length=255)
    request_count = models.IntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering=['-date', '-created_at']
        indexes = [
            models.Index(fields=['customer', 'date']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['status_code']),
            models.Index(fields=['date']),
            models.Index(fields=['customer', 'date', 'endpoint'])
        ]
        unique_together = [['customer', 'date', 'endpoint', 'method']]
        
def __str__(self):
    return f"{self.customer.name} - {self.endpoint} - {self.date}"
