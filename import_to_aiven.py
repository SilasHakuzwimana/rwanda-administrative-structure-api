#!/usr/bin/env python3
import os
import django
import re
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_admin_api.settings')
django.setup()

from location.models import Country, Province, District, Sector, Cell, Village
from django.db import transaction

def parse_sql_file(sql_file):
    """Extract data from SQL file"""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {}
    tables = ['countries', 'provinces', 'districts', 'sectors', 'cells', 'villages']
    
    for table in tables:
        # Find INSERT statements for this table
        pattern = rf"INSERT INTO `{table}` \(.*?\) VALUES\s+(.*?);"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        records = []
        for match in matches:
            # Parse each value row
            value_rows = re.findall(r'\(([^()]+(?:\([^()]*\)[^()]*)*)\)', match)
            for row in value_rows:
                # Parse CSV values
                values = []
                current = []
                in_quote = False
                for char in row:
                    if char == "'" and not in_quote:
                        in_quote = True
                        current.append(char)
                    elif char == "'" and in_quote:
                        in_quote = False
                        current.append(char)
                    elif char == ',' and not in_quote:
                        val = ''.join(current).strip()
                        if val == 'NULL' or val == '':
                            values.append(None)
                        elif val.startswith("'") and val.endswith("'"):
                            values.append(val[1:-1])
                        else:
                            values.append(val)
                        current = []
                    else:
                        current.append(char)
                if current:
                    val = ''.join(current).strip()
                    if val == 'NULL' or val == '':
                        values.append(None)
                    elif val.startswith("'") and val.endswith("'"):
                        values.append(val[1:-1])
                    else:
                        values.append(val)
                if values:
                    records.append({
                        'id': int(values[0]) if values[0] and values[0] != 'NULL' else None,
                        'name': values[1] if len(values) > 1 else None,
                        'parent_id': int(values[2]) if len(values) > 2 and values[2] and values[2] != 'NULL' else None
                    })
        
        data[table] = records
        print(f"📊 Found {len(records)} records in {table}")
    
    return data

@transaction.atomic
def import_data(sql_file):
    """Import data to Django models"""
    
    print("🚀 Starting data import to Aiven PostgreSQL...")
    print("="*50)
    
    # Parse SQL file
    data = parse_sql_file(sql_file)
    
    # First, create or get Rwanda country
    rwanda, created = Country.objects.get_or_create(
        name='Rwanda',
        defaults={'name': 'Rwanda'}
    )
    if created:
        print(f"✓ Created country: {rwanda.name}")
    else:
        print(f"✓ Found existing country: {rwanda.name}")
    
    # Clear existing data to avoid duplicates (optional)
    # Uncomment if you want fresh import
    # print("Clearing existing data...")
    # Village.objects.all().delete()
    # Cell.objects.all().delete()
    # Sector.objects.all().delete()
    # District.objects.all().delete()
    # Province.objects.all().delete()
    
    # Import provinces
    print("\n📥 Importing provinces...")
    provinces_created = 0
    province_map = {}
    
    for record in data['provinces']:
        if record['name']:
            obj, created = Province.objects.get_or_create(
                name=record['name'],
                country=rwanda
            )
            if created:
                provinces_created += 1
                print(f"  ✓ Added province: {record['name']}")
            province_map[record['id']] = obj
    
    print(f"✅ Provinces: {provinces_created} new, {Province.objects.filter(country=rwanda).count()} total")
    
    # Import districts
    print("\n📥 Importing districts...")
    districts_created = 0
    district_map = {}
    
    for record in data['districts']:
        if record['name'] and record['parent_id']:
            province = province_map.get(record['parent_id'])
            if province:
                obj, created = District.objects.get_or_create(
                    name=record['name'],
                    province=province
                )
                if created:
                    districts_created += 1
                    if districts_created <= 30:
                        print(f"  ✓ Added district: {record['name']} in {province.name}")
                district_map[record['id']] = obj
    
    print(f"✅ Districts: {districts_created} new, {District.objects.count()} total")
    
    # Import sectors
    print("\n📥 Importing sectors...")
    sectors_created = 0
    sector_map = {}
    
    for record in data['sectors']:
        if record['name'] and record['parent_id']:
            district = district_map.get(record['parent_id'])
            if district:
                obj, created = Sector.objects.get_or_create(
                    name=record['name'],
                    district=district
                )
                if created:
                    sectors_created += 1
                    if sectors_created <= 20:
                        print(f"  ✓ Added sector: {record['name']} in {district.name}")
                sector_map[record['id']] = obj
    
    print(f"✅ Sectors: {sectors_created} new, {Sector.objects.count()} total")
    
    # Import cells
    print("\n📥 Importing cells...")
    cells_created = 0
    cell_map = {}
    
    for record in data['cells']:
        if record['name'] and record['parent_id']:
            sector = sector_map.get(record['parent_id'])
            if sector:
                obj, created = Cell.objects.get_or_create(
                    name=record['name'],
                    sector=sector
                )
                if created:
                    cells_created += 1
                    if cells_created <= 20:
                        print(f"  ✓ Added cell: {record['name']} in {sector.name}")
                cell_map[record['id']] = obj
    
    print(f"✅ Cells: {cells_created} new, {Cell.objects.count()} total")
    
    # Import villages
    print("\n📥 Importing villages...")
    villages_created = 0
    
    for record in data['villages']:
        if record['name'] and record['parent_id']:
            cell = cell_map.get(record['parent_id'])
            if cell:
                obj, created = Village.objects.get_or_create(
                    name=record['name'],
                    cell=cell
                )
                if created:
                    villages_created += 1
                    if villages_created <= 20:
                        print(f"  ✓ Added village: {record['name']} in {cell.name}")
    
    print(f"✅ Villages: {villages_created} new, {Village.objects.count()} total")
    
    # Final statistics
    print("\n" + "="*50)
    print("📊 FINAL STATISTICS - AIVEN POSTGRESQL")
    print("="*50)
    print(f"Countries: {Country.objects.count()}")
    print(f"Provinces: {Province.objects.filter(country=rwanda).count()}")
    print(f"Districts: {District.objects.count()}")
    print(f"Sectors: {Sector.objects.count()}")
    print(f"Cells: {Cell.objects.count()}")
    print(f"Villages: {Village.objects.count()}")
    print("="*50)
    
    return True

def show_sample():
    """Display sample data"""
    print("\n📋 Sample Data from Aiven PostgreSQL:")
    print("-"*50)
    
    try:
        rwanda = Country.objects.get(name='Rwanda')
        provinces = Province.objects.filter(country=rwanda)[:3]
        
        for province in provinces:
            print(f"\n📍 {province.name}:")
            districts = District.objects.filter(province=province)[:2]
            for district in districts:
                sector_count = Sector.objects.filter(district=district).count()
                print(f"  └─ {district.name} ({sector_count} sectors)")
                
                sectors = Sector.objects.filter(district=district)[:2]
                for sector in sectors:
                    cell_count = Cell.objects.filter(sector=sector).count()
                    print(f"      └─ {sector.name} ({cell_count} cells)")
                    
                    cells = Cell.objects.filter(sector=sector)[:1]
                    for cell in cells:
                        village_count = Village.objects.filter(cell=cell).count()
                        print(f"          └─ {cell.name} ({village_count} villages)...")
        
        print("\n✅ Data import verification complete!")
        
    except Country.DoesNotExist:
        print("❌ Rwanda country not found in database")

def verify_data_integrity():
    """Verify data relationships"""
    print("\n🔍 Verifying Data Integrity:")
    print("-"*50)
    
    # Check for orphans
    orphan_districts = District.objects.filter(province__isnull=True).count()
    orphan_sectors = Sector.objects.filter(district__isnull=True).count()
    orphan_cells = Cell.objects.filter(sector__isnull=True).count()
    orphan_villages = Village.objects.filter(cell__isnull=True).count()
    
    print(f"Districts without province: {orphan_districts}")
    print(f"Sectors without district: {orphan_sectors}")
    print(f"Cells without sector: {orphan_cells}")
    print(f"Villages without cell: {orphan_villages}")
    
    if orphan_districts == 0 and orphan_sectors == 0 and orphan_cells == 0 and orphan_villages == 0:
        print("✅ All data relationships are intact!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_to_aiven.py <sql_file>")
        print("Example: python import_to_aiven.py if0_36150530_rwanda_data_db.sql")
        sys.exit(1)
    
    # Import data
    success = import_data(sys.argv[1])
    
    if success:
        verify_data_integrity()
        show_sample()
        print("\n🎉 Import to Aiven PostgreSQL completed successfully!")
    else:
        print("\n❌ Import failed!")
        sys.exit(1)
