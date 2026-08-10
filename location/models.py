# location/models.py
from django.db import models
from django.core.cache import cache
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import secrets
import hashlib


# ============================================
# Base Model with Common Functionality
# ============================================
class BaseModel(models.Model):
    """Abstract base model with common fields and caching"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        abstract = True
    
    @classmethod
    def get_cache_key(cls, prefix, *args):
        """Generate cache key with prefix"""
        key_parts = [prefix] + [str(arg) for arg in args if arg is not None]
        return '_'.join(key_parts)
    
    @classmethod
    def invalidate_cache(cls, pattern):
        """Invalidate cache by pattern"""
        cache.delete_pattern(f'{pattern}_*')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._invalidate_cache()
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Override in child classes"""
        pass


# ============================================
# Country Model
# ============================================
class Country(BaseModel):
    name = models.CharField(max_length=100, db_index=True, unique=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Countries"
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_all_cached(cls):
        """Get all countries with caching"""
        cache_key = 'countries_all'
        countries = cache.get(cache_key)
        if countries is None:
            countries = list(cls.objects.all())
            cache.set(cache_key, countries, 86400)  # 24 hours
        return countries
    
    @classmethod
    def get_by_name_cached(cls, name):
        """Get country by name with caching"""
        cache_key = f'country_name_{name.lower()}'
        country = cache.get(cache_key)
        if country is None:
            try:
                country = cls.objects.get(name__iexact=name)
                cache.set(cache_key, country, 86400)
            except cls.DoesNotExist:
                country = None
        return country
    
    def _invalidate_cache(self):
        cache.delete('countries_all')
        cache.delete_pattern('country_name_*')


# ============================================
# Province Model
# ============================================
class Province(BaseModel):
    name = models.CharField(max_length=100, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, db_index=True, related_name='provinces')
    
    class Meta:
        unique_together = ('name', 'country')
        ordering = ['name']
        indexes = [
            models.Index(fields=['country', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.country.name})"
    
    @classmethod
    def get_all_cached(cls):
        """Get all provinces with caching"""
        cache_key = 'provinces_all'
        provinces = cache.get(cache_key)
        if provinces is None:
            provinces = list(cls.objects.select_related('country').all())
            cache.set(cache_key, provinces, 3600)  # 1 hour
        return provinces
    
    @classmethod
    def get_by_country_cached(cls, country_id):
        """Get provinces by country with caching"""
        cache_key = f'provinces_country_{country_id}'
        provinces = cache.get(cache_key)
        if provinces is None:
            provinces = list(cls.objects.filter(country_id=country_id))
            cache.set(cache_key, provinces, 3600)
        return provinces
    
    @classmethod
    def get_by_name_cached(cls, name, country_id=None):
        """Get province by name with caching"""
        cache_key = f'province_name_{name.lower()}_{country_id or "all"}'
        province = cache.get(cache_key)
        if province is None:
            queryset = cls.objects.filter(name__iexact=name)
            if country_id:
                queryset = queryset.filter(country_id=country_id)
            province = queryset.first()
            cache.set(cache_key, province, 3600)
        return province
    
    def _invalidate_cache(self):
        cache.delete('provinces_all')
        cache.delete(f'provinces_country_{self.country_id}')
        cache.delete_pattern(f'province_name_*_{self.country_id}')
        cache.delete_pattern(f'province_name_*_all')


# ============================================
# District Model
# ============================================
class District(BaseModel):
    name = models.CharField(max_length=100, db_index=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, db_index=True, related_name='districts')
    
    class Meta:
        unique_together = ('name', 'province')
        ordering = ['name']
        indexes = [
            models.Index(fields=['province', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.province.name})"
    
    @classmethod
    def get_all_cached(cls):
        """Get all districts with caching"""
        cache_key = 'districts_all'
        districts = cache.get(cache_key)
        if districts is None:
            districts = list(cls.objects.select_related('province', 'province__country').all())
            cache.set(cache_key, districts, 3600)
        return districts
    
    @classmethod
    def get_by_province_cached(cls, province_id):
        """Get districts by province with caching"""
        cache_key = f'districts_province_{province_id}'
        districts = cache.get(cache_key)
        if districts is None:
            districts = list(cls.objects.filter(province_id=province_id))
            cache.set(cache_key, districts, 3600)
        return districts
    
    def _invalidate_cache(self):
        cache.delete(f'districts_province_{self.province_id}')
        cache.delete('districts_all')


# ============================================
# Sector Model
# ============================================
class Sector(BaseModel):
    name = models.CharField(max_length=100, db_index=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, db_index=True, related_name='sectors')
    
    class Meta:
        unique_together = ('name', 'district')
        ordering = ['name']
        indexes = [
            models.Index(fields=['district', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.district.name})"
    
    @classmethod
    def get_all_cached(cls):
        """Get all sectors with caching"""
        cache_key = 'sectors_all'
        sectors = cache.get(cache_key)
        if sectors is None:
            sectors = list(cls.objects.select_related('district', 'district__province').all())
            cache.set(cache_key, sectors, 3600)
        return sectors
    
    @classmethod
    def get_by_district_cached(cls, district_id):
        """Get sectors by district with caching"""
        cache_key = f'sectors_district_{district_id}'
        sectors = cache.get(cache_key)
        if sectors is None:
            sectors = list(cls.objects.filter(district_id=district_id))
            cache.set(cache_key, sectors, 1800)  # 30 minutes
        return sectors
    
    def _invalidate_cache(self):
        cache.delete(f'sectors_district_{self.district_id}')
        cache.delete('sectors_all')


# ============================================
# Cell Model
# ============================================
class Cell(BaseModel):
    name = models.CharField(max_length=100, db_index=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, db_index=True, related_name='cells')
    
    class Meta:
        unique_together = ('name', 'sector')
        ordering = ['name']
        indexes = [
            models.Index(fields=['sector', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sector.name})"
    
    @classmethod
    def get_all_cached(cls):
        """Get all cells with caching"""
        cache_key = 'cells_all'
        cells = cache.get(cache_key)
        if cells is None:
            cells = list(cls.objects.select_related('sector', 'sector__district').all())
            cache.set(cache_key, cells, 3600)
        return cells
    
    @classmethod
    def get_by_sector_cached(cls, sector_id):
        """Get cells by sector with caching"""
        cache_key = f'cells_sector_{sector_id}'
        cells = cache.get(cache_key)
        if cells is None:
            cells = list(cls.objects.filter(sector_id=sector_id))
            cache.set(cache_key, cells, 900)  # 15 minutes
        return cells
    
    def _invalidate_cache(self):
        cache.delete(f'cells_sector_{self.sector_id}')
        cache.delete('cells_all')


# ============================================
# Village Model
# ============================================
class Village(BaseModel):
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True, blank=True, null=True)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, db_index=True, related_name='villages')
    
    class Meta:
        unique_together = ('name', 'cell')
        ordering = ['name']
        indexes = [
            models.Index(fields=['cell', 'name']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.generate_code()
        super().save(*args, **kwargs)
        self._invalidate_cache()
    
    def generate_code(self):
        """Generate a unique code for the village"""
        base_code = slugify(self.name).upper()[:8]
        if not base_code:
            base_code = "VIL"
        
        # Ensure uniqueness
        counter = 1
        code = base_code
        while Village.objects.filter(code=code).exclude(pk=self.pk).exists():
            code = f"{base_code}{counter}"
            counter += 1
        self.code = code
    
    @classmethod
    def get_all_cached(cls):
        """Get all villages with caching"""
        cache_key = 'villages_all'
        villages = cache.get(cache_key)
        if villages is None:
            villages = list(cls.objects.select_related(
                'cell',
                'cell__sector',
                'cell__sector__district',
                'cell__sector__district__province',
                'cell__sector__district__province__country'
            ).all())
            cache.set(cache_key, villages, 300)  # 5 minutes
        return villages
    
    @classmethod
    def get_by_cell_cached(cls, cell_id):
        """Get villages by cell with caching"""
        cache_key = f'villages_cell_{cell_id}'
        villages = cache.get(cache_key)
        if villages is None:
            villages = list(cls.objects.filter(cell_id=cell_id))
            cache.set(cache_key, villages, 300)
        return villages
    
    @classmethod
    def get_by_code_cached(cls, code):
        """Get village by code with caching"""
        cache_key = f'village_code_{code.upper()}'
        village = cache.get(cache_key)
        if village is None:
            village = cls.objects.filter(code__iexact=code).first()
            cache.set(cache_key, village, 3600)
        return village
    
    def _invalidate_cache(self):
        cache.delete(f'villages_cell_{self.cell_id}')
        cache.delete('villages_all')
        if self.code:
            cache.delete(f'village_code_{self.code.upper()}')


# ============================================
# API Customer Models
# ============================================
class APICustomer(BaseModel):
    """Customer who subscribes to the API"""
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='free', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['plan', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.plan} ({self.email})"
    
    @classmethod
    def get_by_email_cached(cls, email):
        """Get customer by email with caching"""
        cache_key = f'customer_email_{email.lower()}'
        customer = cache.get(cache_key)
        if customer is None:
            customer = cls.objects.filter(email__iexact=email).first()
            cache.set(cache_key, customer, 3600)
        return customer
    
    @classmethod
    def get_active_customers_cached(cls):
        """Get all active customers with caching"""
        cache_key = 'customers_active'
        customers = cache.get(cache_key)
        if customers is None:
            customers = list(cls.objects.filter(is_active=True))
            cache.set(cache_key, customers, 300)
        return customers
    
    def _invalidate_cache(self):
        cache.delete(f'customer_email_{self.email.lower()}')
        cache.delete('customers_active')


class APIKey(BaseModel):
    """API keys for customers (each customer can have multiple keys)"""
    customer = models.ForeignKey(APICustomer, on_delete=models.CASCADE, related_name='api_keys', db_index=True)
    name = models.CharField(max_length=100, help_text="e.g., Production Key, Testing Key")
    key = models.CharField(max_length=64, unique=True, editable=False, db_index=True)
    key_prefix = models.CharField(max_length=8, editable=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key_prefix = secrets.token_hex(16)[:8]
            self.key = f"wars_{self.customer.plan}_{self.key_prefix}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['key_prefix']),
            models.Index(fields=['key']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - {self.name} ({self.key_prefix})"
    
    @classmethod
    def get_by_key_cached(cls, key):
        """Get API key by key value with caching"""
        cache_key = f'apikey_{key}'
        api_key = cache.get(cache_key)
        if api_key is None:
            api_key = cls.objects.filter(key=key, is_active=True).first()
            cache.set(cache_key, api_key, 300)
        return api_key
    
    def _invalidate_cache(self):
        cache.delete(f'apikey_{self.key}')
        cache.delete_pattern(f'apikey_prefix_{self.key_prefix}_*')


class AllowedOrigin(BaseModel):
    """Allowed origins (domains) for each customer"""
    customer = models.ForeignKey(APICustomer, on_delete=models.CASCADE, related_name='allowed_origins', db_index=True)
    origin = models.CharField(max_length=255, help_text="e.g., https://myapp.com or http://localhost:3000", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        unique_together = ['customer', 'origin']
        ordering = ['origin']
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['origin']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - {self.origin}"
    
    @classmethod
    def get_by_customer_cached(cls, customer_id):
        """Get allowed origins by customer with caching"""
        cache_key = f'origins_customer_{customer_id}'
        origins = cache.get(cache_key)
        if origins is None:
            origins = list(cls.objects.filter(customer_id=customer_id, is_active=True))
            cache.set(cache_key, origins, 3600)
        return origins
    
    def _invalidate_cache(self):
        cache.delete(f'origins_customer_{self.customer_id}')


class APIUsage(BaseModel):
    """Track usage per customer for billing"""
    customer = models.ForeignKey(APICustomer, on_delete=models.CASCADE, related_name='api_usage', db_index=True)
    date = models.DateField(auto_now_add=True, db_index=True)
    endpoint = models.CharField(max_length=200, db_index=True)
    method = models.CharField(max_length=10, db_index=True)
    status_code = models.IntegerField(db_index=True)
    origin = models.CharField(max_length=255, db_index=True)
    request_count = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['customer', 'date']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['status_code']),
            models.Index(fields=['date']),
            models.Index(fields=['customer', 'date', 'endpoint']),
            models.Index(fields=['customer', 'date', 'status_code']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['customer', 'date', 'endpoint', 'method']]
    
    def __str__(self):
        return f"{self.customer.name} - {self.endpoint} - {self.date}"
    
    @classmethod
    def get_usage_by_customer_cached(cls, customer_id, days=30):
        """Get usage for customer with caching"""
        cache_key = f'usage_customer_{customer_id}_days_{days}'
        usage = cache.get(cache_key)
        if usage is None:
            start_date = timezone.now().date() - timedelta(days=days)
            usage = list(cls.objects.filter(
                customer_id=customer_id,
                date__gte=start_date
            ).order_by('-date'))
            cache.set(cache_key, usage, 300)  # 5 minutes
        return usage
    
    @classmethod
    def get_usage_summary_cached(cls, customer_id, days=30):
        """Get usage summary with caching"""
        cache_key = f'usage_summary_{customer_id}_days_{days}'
        summary = cache.get(cache_key)
        if summary is None:
            start_date = timezone.now().date() - timedelta(days=days)
            summary = {
                'total_requests': cls.objects.filter(
                    customer_id=customer_id,
                    date__gte=start_date
                ).aggregate(total=models.Sum('request_count'))['total'] or 0,
                'unique_endpoints': cls.objects.filter(
                    customer_id=customer_id,
                    date__gte=start_date
                ).values('endpoint').distinct().count(),
                'status_codes': cls.objects.filter(
                    customer_id=customer_id,
                    date__gte=start_date
                ).values('status_code').annotate(
                    count=models.Count('id')
                ).order_by('-count'),
            }
            cache.set(cache_key, summary, 300)
        return summary
    
    def _invalidate_cache(self):
        cache.delete_pattern(f'usage_customer_{self.customer_id}_*')
        cache.delete_pattern(f'usage_summary_{self.customer_id}_*')


# ============================================
# Cache Test Helper
# ============================================
def test_cache_connection():
    """Test if Redis cache is working"""
    try:
        test_key = 'cache_test'
        test_value = 'working'
        cache.set(test_key, test_value, 5)
        result = cache.get(test_key)
        cache.delete(test_key)
        return result == test_value
    except Exception as e:
        print(f"⚠️ Cache connection error: {e}")
        return False