from django.contrib import admin
from django.db import models
from .models import (
    APICustomer, APIKey, APIUsage, AllowedOrigin,
    Country, Province, District, Sector, Cell, Village
)

# ============================================
# Base Admin Class with Common Optimizations
# ============================================
class BaseAdmin(admin.ModelAdmin):
    """Base admin with common optimizations"""
    actions = ["delete_selected"]
    list_per_page = 50  # ✅ Increased from 10 for better UX
    show_full_result_count = False  # ✅ Faster count for large datasets


# ============================================
# Location Models - Optimized
# ============================================

@admin.register(Country)
class CountryAdmin(BaseAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)
    list_editable = ("name",)
    list_per_page = 20


@admin.register(Province)
class ProvinceAdmin(BaseAdmin):
    list_display = ("id", "name", "country")
    search_fields = ("name", "country__name")
    list_filter = ("country",)
    ordering = ("name",)
    list_editable = ("name", "country")
    list_select_related = ("country",)  # ✅ Added: 1 query instead of N+1


@admin.register(District)
class DistrictAdmin(BaseAdmin):
    list_display = ("id", "name", "province", "province_country")
    search_fields = ("name", "province__name")
    list_filter = ("province",)
    ordering = ("name",)
    list_editable = ("name", "province")
    list_select_related = ("province", "province__country")  # ✅ Added
    
    def province_country(self, obj):
        return obj.province.country.name
    province_country.short_description = "Country"


@admin.register(Sector)
class SectorAdmin(BaseAdmin):
    list_display = ("id", "name", "district", "district_province", "district_country")
    search_fields = ("name", "district__name")
    list_filter = ("district",)
    ordering = ("name",)
    list_editable = ("name", "district")
    list_select_related = (
        "district",
        "district__province",
        "district__province__country"
    )  # ✅ Added: Fixes N+1 problem!
    
    def district_province(self, obj):
        return obj.district.province.name
    district_province.short_description = "Province"
    
    def district_country(self, obj):
        return obj.district.province.country.name
    district_country.short_description = "Country"


@admin.register(Cell)
class CellAdmin(BaseAdmin):
    list_display = ("id", "name", "sector", "sector_district", "sector_province")
    search_fields = ("name", "sector__name")
    list_filter = ("sector",)
    ordering = ("name",)
    list_editable = ("name", "sector")
    list_select_related = (
        "sector",
        "sector__district",
        "sector__district__province",
        "sector__district__province__country"
    )  # ✅ Added
    
    def sector_district(self, obj):
        return obj.sector.district.name
    sector_district.short_description = "District"
    
    def sector_province(self, obj):
        return obj.sector.district.province.name
    sector_province.short_description = "Province"


@admin.register(Village)
class VillageAdmin(BaseAdmin):
    list_display = ("id", "name", "code", "cell", "cell_sector", "cell_district")
    search_fields = ("name", "code", "cell__name")
    list_filter = ("cell",)
    ordering = ("name",)
    list_editable = ("name", "code", "cell")
    list_select_related = (
        "cell",
        "cell__sector",
        "cell__sector__district",
        "cell__sector__district__province"
    )  # ✅ Added
    list_per_page = 25  # Villages are large, use smaller page size
    
    def cell_sector(self, obj):
        return obj.cell.sector.name
    cell_sector.short_description = "Sector"
    
    def cell_district(self, obj):
        return obj.cell.sector.district.name
    cell_district.short_description = "District"


# ============================================
# API Models - Optimized
# ============================================

@admin.register(APICustomer)
class APICustomerAdmin(BaseAdmin):
    list_display = ("id", "email", "name", "plan", "is_active", "created_at")
    list_filter = ("plan", "is_active", "created_at")
    search_fields = ("email", "name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    ordering = ("-created_at",)
    
    # ✅ Add date hierarchy for better navigation
    date_hierarchy = "created_at"


@admin.register(APIKey)
class APIKeyAdmin(BaseAdmin):
    list_display = ("id", "key_prefix", "customer", "name", "is_active", "created_at", "last_used_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("key", "name", "key_prefix", "customer__email")
    readonly_fields = ("created_at", "key", "key_prefix")
    list_per_page = 25
    ordering = ("-created_at",)
    list_select_related = ("customer",)  # ✅ Added


@admin.register(AllowedOrigin)
class AllowedOriginAdmin(BaseAdmin):
    list_display = ("id", "origin", "customer", "is_active", "created_at")
    list_filter = ("is_active", "customer")
    search_fields = ("origin", "customer__email")
    list_per_page = 25
    ordering = ("origin",)
    list_select_related = ("customer",)  # ✅ Added


@admin.register(APIUsage)
class APIUsageAdmin(BaseAdmin):
    list_display = (
        "id", "customer", "endpoint", "method", 
        "status_code", "request_count", "date", "created_at"
    )
    list_filter = ("method", "status_code", "date", "created_at")
    search_fields = ("endpoint", "customer__email", "origin")
    readonly_fields = ("date", "created_at")
    list_per_page = 25
    ordering = ("-date", "-created_at")
    list_select_related = ("customer",)  # ✅ Added
    
    # ✅ Add date hierarchy
    date_hierarchy = "date"
    
    # ✅ Add totals in admin
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("customer")