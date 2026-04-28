#!/usr/bin/env python3
"""
Complete diagnostic script for Aiven PostgreSQL database
Checks all location data, relationships, and data integrity
"""

import os
import django
import sys
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_admin_api.settings')
django.setup()

from location.models import Country, Province, District, Sector, Cell, Village
from django.db import connection
from django.db.models import Count, Q

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def check_connection():
    """Test database connection"""
    print_section("1. DATABASE CONNECTION")
    try:
        connection.ensure_connection()
        print("✅ Connected to Aiven PostgreSQL")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   Version: {version[:80]}...")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_counts():
    """Check record counts for all models"""
    print_section("2. RECORD COUNTS")
    
    counts = {
        'Countries': Country.objects.count(),
        'Provinces': Province.objects.count(),
        'Districts': District.objects.count(),
        'Sectors': Sector.objects.count(),
        'Cells': Cell.objects.count(),
        'Villages': Village.objects.count(),
    }
    
    expected = {
        'Countries': 1,
        'Provinces': 5,
        'Districts': 30,
        'Sectors': 416,
        'Cells': 2148,
        'Villages': 14840,
    }
    
    print("\n📊 Current vs Expected:")
    print("-" * 50)
    for name, count in counts.items():
        expected_count = expected.get(name, 0)
        status = "✅" if count == expected_count else "⚠️" if count > 0 else "❌"
        print(f"{status} {name:12}: {count:6,} / {expected_count:6,}")
    
    # Calculate completion percentage
    if counts['Villages'] > 0:
        total_current = sum(counts.values())
        total_expected = sum(expected.values())
        percent = (total_current / total_expected) * 100
        print(f"\n📈 Overall completion: {percent:.1f}%")
        print(f"   Total records: {total_current:,} / {total_expected:,}")
    
    return counts

def check_hierarchy():
    """Check hierarchical relationships"""
    print_section("3. HIERARCHY VALIDATION")
    
    # Check for orphans (records with missing parents)
    orphans = {
        'Provinces without country': Province.objects.filter(country__isnull=True).count(),
        'Districts without province': District.objects.filter(province__isnull=True).count(),
        'Sectors without district': Sector.objects.filter(district__isnull=True).count(),
        'Cells without sector': Cell.objects.filter(sector__isnull=True).count(),
        'Villages without cell': Village.objects.filter(cell__isnull=True).count(),
    }
    
    print("\n🔗 Orphan Records (missing parent):")
    print("-" * 50)
    has_orphans = False
    for name, count in orphans.items():
        status = "✅" if count == 0 else "❌"
        print(f"{status} {name}: {count}")
        if count > 0:
            has_orphans = True
    
    if not has_orphans:
        print("\n✅ All hierarchical relationships are intact!")
    
    return orphans

def check_province_distribution():
    """Check province-level distribution"""
    print_section("4. PROVINCE DISTRIBUTION")
    
    try:
        rwanda = Country.objects.get(name='Rwanda')
        provinces = Province.objects.filter(country=rwanda)
        
        print(f"\n📍 Country: {rwanda.name}")
        print(f"   Total Provinces: {provinces.count()}")
        print("\n📊 Province Details:")
        print("-" * 60)
        
        for province in provinces.order_by('name'):
            district_count = District.objects.filter(province=province).count()
            sector_count = Sector.objects.filter(district__province=province).count()
            cell_count = Cell.objects.filter(sector__district__province=province).count()
            village_count = Village.objects.filter(cell__sector__district__province=province).count()
            
            print(f"\n  📍 {province.name}:")
            print(f"     Districts: {district_count:3}")
            print(f"     Sectors:   {sector_count:4}")
            print(f"     Cells:     {cell_count:5}")
            print(f"     Villages:  {village_count:6}")
            
    except Country.DoesNotExist:
        print("❌ Rwanda not found in database!")

def check_district_distribution():
    """Show district distribution by province"""
    print_section("5. DISTRICT DISTRIBUTION")
    
    provinces = Province.objects.annotate(
        district_count=Count('districts')
    ).order_by('-district_count')
    
    print("\n📊 Districts per Province:")
    print("-" * 50)
    for province in provinces:
        bar = "█" * min(province.district_count, 30)
        print(f"  {province.name:20}: {province.district_count:2} districts {bar}")

def check_sample_data():
    """Show sample data from each level"""
    print_section("6. SAMPLE DATA")
    
    # Get a random village with full hierarchy
    village = Village.objects.select_related(
        'cell__sector__district__province__country'
    ).first()
    
    if village:
        print("\n🏘️  Full Hierarchy Example:")
        print("-" * 50)
        print(f"  Country:  {village.cell.sector.district.province.country.name}")
        print(f"  Province: {village.cell.sector.district.province.name}")
        print(f"  District: {village.cell.sector.district.name}")
        print(f"  Sector:   {village.cell.sector.name}")
        print(f"  Cell:     {village.cell.name}")
        print(f"  Village:  {village.name}")
    
    # Show some random villages
    print("\n📋 Random Village Samples:")
    print("-" * 50)
    random_villages = Village.objects.select_related('cell').order_by('?')[:10]
    for village in random_villages:
        print(f"  • {village.name} ({village.cell.name})")

def check_data_integrity():
    """Check for potential data issues"""
    print_section("7. DATA INTEGRITY CHECKS")
    
    issues = []
    
    # Check for duplicate names within same parent
    duplicate_districts = District.objects.values('name', 'province').annotate(
        cnt=Count('id')
    ).filter(cnt__gt=1)
    
    if duplicate_districts:
        issues.append(f"⚠️ Found {duplicate_districts.count()} duplicate district names within same province")
    
    duplicate_sectors = Sector.objects.values('name', 'district').annotate(
        cnt=Count('id')
    ).filter(cnt__gt=1)
    
    if duplicate_sectors:
        issues.append(f"⚠️ Found {duplicate_sectors.count()} duplicate sector names within same district")
    
    # Check for empty names
    empty_names = []
    if Country.objects.filter(name__isnull=True).exists():
        empty_names.append("Countries")
    if Province.objects.filter(name__isnull=True).exists():
        empty_names.append("Provinces")
    if District.objects.filter(name__isnull=True).exists():
        empty_names.append("Districts")
    
    if empty_names:
        issues.append(f"❌ Found records with empty names in: {', '.join(empty_names)}")
    
    if issues:
        print("\n⚠️ Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ No data integrity issues found!")

def check_missing_relationships():
    """Check for missing hierarchical relationships"""
    print_section("8. RELATIONSHIP COMPLETENESS")
    
    # Check for districts without sectors
    districts_without_sectors = District.objects.annotate(
        sector_count=Count('sectors')
    ).filter(sector_count=0)
    
    if districts_without_sectors:
        print(f"\n⚠️ Districts with no sectors: {districts_without_sectors.count()}")
        for district in districts_without_sectors[:5]:
            print(f"  • {district.name} ({district.province.name})")
    else:
        print("\n✅ All districts have sectors")
    
    # Check for sectors without cells
    sectors_without_cells = Sector.objects.annotate(
        cell_count=Count('cells')
    ).filter(cell_count=0)
    
    if sectors_without_cells:
        print(f"\n⚠️ Sectors with no cells: {sectors_without_cells.count()}")
        for sector in sectors_without_cells[:5]:
            print(f"  • {sector.name} ({sector.district.name})")
    else:
        print("✅ All sectors have cells")
    
    # Check for cells without villages
    cells_without_villages = Cell.objects.annotate(
        village_count=Count('villages')
    ).filter(village_count=0)
    
    if cells_without_villages:
        print(f"\n⚠️ Cells with no villages: {cells_without_villages.count()}")
        for cell in cells_without_villages[:5]:
            print(f"  • {cell.name} ({cell.sector.name})")
    else:
        print("✅ All cells have villages")

def generate_summary():
    """Generate final summary"""
    print_section("9. FINAL SUMMARY")
    
    counts = {
        'Countries': Country.objects.count(),
        'Provinces': Province.objects.count(),
        'Districts': District.objects.count(),
        'Sectors': Sector.objects.count(),
        'Cells': Cell.objects.count(),
        'Villages': Village.objects.count(),
    }
    
    total_records = sum(counts.values())
    
    print(f"\n📊 Database: Aiven PostgreSQL")
    print(f"📅 Check Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Total Records: {total_records:,}")
    
    print("\n🎯 Target vs Current:")
    print("-" * 40)
    print(f"  Countries:  1     / {counts['Countries']}")
    print(f"  Provinces:  5     / {counts['Provinces']}")
    print(f"  Districts:  30    / {counts['Districts']}")
    print(f"  Sectors:    416   / {counts['Sectors']}")
    print(f"  Cells:      2,148 / {counts['Cells']}")
    print(f"  Villages:   14,840/ {counts['Villages']}")
    
    if counts['Villages'] == 14840:
        print("\n🎉 PERFECT! All data has been successfully imported!")
    elif counts['Villages'] > 0:
        remaining = 14840 - counts['Villages']
        print(f"\n⚠️ Still need to import {remaining:,} villages ({remaining/14840*100:.1f}% remaining)")
    else:
        print("\n❌ No villages found in database")
    
    # Recommendations
    if counts['Villages'] < 14840:
        print("\n💡 Recommendations:")
        print("  1. Run the import script again to import missing villages")
        print("  2. Check cell mapping between SQL and database")
        print("  3. Verify that all cells were imported correctly")

def main():
    """Run all checks"""
    print("\n" + "🔍" * 35)
    print("   AIVEN POSTGRESQL - COMPLETE DATABASE DIAGNOSTIC")
    print("🔍" * 35)
    
    # Run all checks
    if not check_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    check_counts()
    check_hierarchy()
    check_province_distribution()
    check_district_distribution()
    check_sample_data()
    check_data_integrity()
    check_missing_relationships()
    generate_summary()
    
    print("\n" + "="*70)
    print(" Diagnostic Complete")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
