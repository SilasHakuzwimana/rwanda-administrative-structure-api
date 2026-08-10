from django.contrib import admin
from .models import APICustomer, APIKey, APIUsage, AllowedOrigin, Country, Province, District, Sector, Cell, Village
# Register your models here.

#Location Models
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)
    list_per_page = 10
    list_editable = ("name",)
    actions = ["delete_selected"]
    
@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)
    list_per_page = 10
    list_editable = ("name",)
    actions = ["delete_selected"]
    
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "province")
    search_fields = ("name",)
    list_filter = ("name", "province")
    ordering = ("name",)
    list_per_page = 10
    list_editable = ("name", "province")
    actions = ["delete_selected"]
    
@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "district")
    search_fields = ("name",)
    list_filter = ("name", "district")
    ordering = ("name",)
    list_per_page = 10
    list_editable = ("name", "district")
    actions = ["delete_selected"]

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sector")
    search_fields = ("name",)
    list_filter = ("name", "sector")
    ordering = ("name",)
    list_per_page = 10
    list_editable = ("name", "sector")
    actions = ["delete_selected"]

@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cell")
    search_fields = ("name",)
    list_filter = ("name", "cell")
    ordering = ("name",)
    list_per_page = 10
    list_editable = ("name", "cell")
    actions = ["delete_selected"]
    

# API models
@admin.register(APICustomer)
class APICustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'plan', 'is_active', 'created_at')
    list_filter = ('plan', 'is_active')
    search_fields = ('email', 'name')
    readonly_fields = ('created_at',)

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'customer', 'name', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('is_active',)
    search_fields = ('key', 'name', 'customer__email')
    readonly_fields = ('created_at', 'last_used_at')

@admin.register(AllowedOrigin)
class AllowedOriginAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin', 'customer', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('origin', 'customer__email')

@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'endpoint', 'method', 'status_code', 'date')
    list_filter = ('method', 'status_code', 'date')
    search_fields = ('endpoint', 'customer__email')
    readonly_fields = ('date',)