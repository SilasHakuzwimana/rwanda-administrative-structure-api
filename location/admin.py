from django.contrib import admin
from .models import Country, Province, District, Sector, Cell, Village
# Register your models here.

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
    
