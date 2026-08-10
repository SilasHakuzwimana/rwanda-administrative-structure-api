from django.shortcuts import render
from rest_framework import viewsets
from .models import Country, Province, District, Sector, Cell, Village  # Add Country
from .serializers import *
from django.contrib.auth.models import User
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters  # Add this for search
from rest_framework.response import Response

# Create your views here.

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    
    # Cache for Countries
    def list(self, request, *args, **kwargs):
        cache_key = 'countries_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 3600)
        return response
    
    
class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.select_related('country')
    serializer_class = ProvinceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country']
    search_fields = ['name']

    # Optional: Cache provinces
    def list(self, request, *args, **kwargs):
        cache_key = f'provinces_list_{request.GET.get("country", "all")}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 3600)
        return response

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.select_related('province', 'province__country')
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['province', 'name']  # Add 'province' here
    search_fields = ['name']


class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.select_related('district', 'district__province', 'district__province__country')
    serializer_class = SectorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['district', 'name']
    search_fields = ['name']


class CellViewSet(viewsets.ModelViewSet):
    queryset = Cell.objects.select_related('sector', 'sector__district', 'sector__district__province')
    serializer_class = CellSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sector', 'name']
    search_fields = ['name']


class VillageViewSet(viewsets.ModelViewSet):
    queryset = Village.objects.select_related('cell','cell__sector','cell__sector__district','cell__sector__district__province')
    serializer_class = VillageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cell', 'cell__sector', 'cell__sector', 'cell__sector__district', 'cell__sector__district__province', 'name']
    search_fields = ['name']
    ordering_fields =['name', 'created_at'],
    ordering =['name']