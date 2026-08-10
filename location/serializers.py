# location/serializers.py

from rest_framework import serializers
from .models import Country, Province, District, Sector, Cell, Village
from django.contrib.auth.models import User


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
        # fields = ['id', 'name']  # Specify the fields you want to include

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = "__all__"


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"


class CellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = "__all__"


class VillageSerializer(serializers.ModelSerializer):
    cell_name = serializers.CharField(source='cell.name', read_only=True)
    sector_name=serializers.CharField(source='cell.sector.name', read_only=True)
    district_name=serializers.CharField(source='cell.sector.district.name', read_only=True)
    province_name = serializers.CharField(source='cell.sector.district.province.name', read_only=True)
    country_name = serializers.CharField(source='cell.sector.district.province.country.name', read_only=True)
    class Meta:
        model = Village
        fields = ['id', 'name', 'code', 'cell_name', 'sector_name', 'district_name', 'province_name', 'country_name']
