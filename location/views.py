from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework import filters
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

from .models import Country, Province, District, Sector, Cell, Village
from .serializers import *


# ============================================
# Custom Pagination
# ============================================
class CustomPagination(PageNumberPagination):
    """Custom pagination with configurable page size"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


# ============================================
# Base ViewSet with Common Functionality
# ============================================
class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with caching and throttling"""
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    cache_timeout = 3600  # 1 hour default
    pagination_class = CustomPagination
    
    def get_cache_key(self, request):
        """Generate cache key from request"""
        query_params = sorted(request.GET.items())
        return f'{self.__class__.__name__}_{hash(str(query_params))}'
    
    def get_cache_prefix(self):
        """Get cache key prefix for this viewset"""
        return self.__class__.__name__.lower().replace('viewset', '')
    
    def invalidate_cache(self, pattern=None):
        """Invalidate cache for this viewset"""
        prefix = self.get_cache_prefix()
        if pattern:
            cache.delete_pattern(f'{prefix}_{pattern}')
        else:
            cache.delete_pattern(f'{prefix}_*')
    
    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, self.cache_timeout)
        return response
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self.invalidate_cache()
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.invalidate_cache()
        return response
    
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self.invalidate_cache()
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self.invalidate_cache()
        return response


# ============================================
# Country ViewSet
# ============================================
class CountryViewSet(BaseViewSet):
    """Country endpoints with 24-hour caching"""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    cache_timeout = 86400  # 24 hours
    
    def get_cache_key(self, request):
        return 'countries_list'


# ============================================
# Province ViewSet
# ============================================
class ProvinceViewSet(BaseViewSet):
    """Province endpoints with 24-hour caching"""
    queryset = Province.objects.select_related('country')
    serializer_class = ProvinceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country']
    search_fields = ['name']
    cache_timeout = 86400  # 24 hours
    
    def get_cache_key(self, request):
        country = request.GET.get('country', 'all')
        return f'provinces_list_{country}'
    
    def invalidate_cache(self):
        """Invalidate all province caches"""
        cache.delete_pattern('provinces_list_*')


# ============================================
# District ViewSet
# ============================================
class DistrictViewSet(BaseViewSet):
    """District endpoints with 1-hour caching"""
    queryset = District.objects.select_related(
        'province', 
        'province__country'
    )
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['province', 'name']
    search_fields = ['name']
    cache_timeout = 3600  # 1 hour
    
    def get_cache_key(self, request):
        province = request.GET.get('province', 'all')
        return f'districts_list_{province}'
    
    def invalidate_cache(self):
        cache.delete_pattern('districts_list_*')


# ============================================
# Sector ViewSet
# ============================================
class SectorViewSet(BaseViewSet):
    """Sector endpoints with 1-hour caching"""
    queryset = Sector.objects.select_related(
        'district', 
        'district__province',
        'district__province__country'
    )
    serializer_class = SectorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['district', 'name']
    search_fields = ['name']
    cache_timeout = 1800  # 30 minutes
    
    def get_cache_key(self, request):
        district = request.GET.get('district', 'all')
        return f'sectors_list_{district}'
    
    def invalidate_cache(self):
        cache.delete_pattern('sectors_list_*')


# ============================================
# Cell ViewSet
# ============================================
class CellViewSet(BaseViewSet):
    """Cell endpoints with 30-minute caching"""
    queryset = Cell.objects.select_related(
        'sector',
        'sector__district',
        'sector__district__province',
        'sector__district__province__country'
    )
    serializer_class = CellSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sector', 'name']
    search_fields = ['name']
    cache_timeout = 900  # 15 minutes
    
    def get_cache_key(self, request):
        sector = request.GET.get('sector', 'all')
        return f'cells_list_{sector}'
    
    def invalidate_cache(self):
        cache.delete_pattern('cells_list_*')


# ============================================
# Village ViewSet
# ============================================
class VillageViewSet(BaseViewSet):
    """Village endpoints with 5-minute caching and optimized queries"""
    queryset = Village.objects.select_related(
        'cell',
        'cell__sector',
        'cell__sector__district',
        'cell__sector__district__province',
        'cell__sector__district__province__country'
    ).only(
        'id',
        'name',
        'cell__name',
        'cell__sector__name',
        'cell__sector__district__name',
        'cell__sector__district__province__name',
        'cell__sector__district__province__country__name'
    )
    serializer_class = VillageSerializer
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_fields = [
        'cell',
        'cell__sector',
        'cell__sector__district',
        'cell__sector__district__province',
        'name'
    ]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    cache_timeout = 300  # 5 minutes
    
    def get_cache_key(self, request):
        # Generate cache key from all query params
        query_params = sorted(request.GET.items())
        # Use simpler cache key for better performance
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '100')
        filters = []
        
        # Include filter params in cache key
        for field in self.filterset_fields:
            value = request.GET.get(field)
            if value:
                filters.append(f'{field}={value}')
        
        filters_str = '_'.join(filters) if filters else 'all'
        return f'villages_list_page{page}_size{page_size}_{filters_str}'
    
    def invalidate_cache(self):
        # Invalidate all village caches (not just one pattern)
        cache.delete_pattern('villages_list_*')