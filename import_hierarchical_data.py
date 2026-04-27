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

# Update the import_hierarchical_data.py script
# Replace the sector import section with this:

@transaction.atomic
def import_data(sql_file):
    """Import data to Django models"""
    
    print("🚀 Starting data import...")
    
    # Parse SQL file
    data = parse_sql_file(sql_file)
    
    # First, get existing Rwanda country
    try:
        rwanda = Country.objects.get(name='Rwanda')
        print(f"✓ Found existing country: {rwanda.name}")
    except Country.DoesNotExist:
        print("❌ Rwanda country not found! Please create it first.")
        return
    
    # Import provinces (skip existing ones)
    provinces_created = 0
    for record in data['provinces']:
        if record['name'] and record['parent_id']:
            obj, created = Province.objects.get_or_create(
                name=record['name'],
                country=rwanda
            )
            if created:
                provinces_created += 1
                print(f"  ✓ Added province: {record['name']}")
    
    print(f"✅ Provinces: {provinces_created} new, {Province.objects.filter(country=rwanda).count()} total")
    
    # Create a mapping of old_id to new object for provinces
    province_map = {}
    for record in data['provinces']:
        if record['name']:
            try:
                province = Province.objects.get(name=record['name'], country=rwanda)
                province_map[record['id']] = province
            except Province.DoesNotExist:
                pass
    
    # Import districts
    districts_created = 0
    district_map = {}  # Map old_id to new district object
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
                    print(f"  ✓ Added district: {record['name']} in {province.name}")
                district_map[record['id']] = obj
    
    print(f"✅ Districts: {districts_created} new, {District.objects.count()} total")
    
    # Import sectors - FIXED to handle duplicates
    sectors_created = 0
    sector_map = {}  # Map old_id to new sector object
    for record in data['sectors']:
        if record['name'] and record['parent_id']:
            district = district_map.get(record['parent_id'])
            if district:
                # Use get_or_create with both name and district to avoid duplicates
                obj, created = Sector.objects.get_or_create(
                    name=record['name'],
                    district=district
                )
                if created:
                    sectors_created += 1
                    if sectors_created <= 20:  # Show first 20 only
                        print(f"  ✓ Added sector: {record['name']} in {district.name}")
                sector_map[record['id']] = obj
    
    print(f"✅ Sectors: {sectors_created} new, {Sector.objects.count()} total")
    
    # Import cells - FIXED to handle duplicates
    cells_created = 0
    cell_map = {}  # Map old_id to new cell object
    for record in data['cells']:
        if record['name'] and record['parent_id']:
            sector = sector_map.get(record['parent_id'])
            if sector:
                # Use get_or_create with both name and sector
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
    
    # Import villages - FIXED to handle duplicates
    villages_created = 0
    for i, record in enumerate(data['villages']):
        if record['name'] and record['parent_id']:
            cell = cell_map.get(record['parent_id'])
            if cell:
                # Use get_or_create with both name and cell
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
    print("📊 FINAL STATISTICS")
    print("="*50)
    print(f"Countries: {Country.objects.count()}")
    print(f"Provinces: {Province.objects.filter(country=rwanda).count()}")
    print(f"Districts: {District.objects.count()}")
    print(f"Sectors: {Sector.objects.count()}")
    print(f"Cells: {Cell.objects.count()}")
    print(f"Villages: {Village.objects.count()}")
    print("="*50)
    
    
def show_sample():
    """Display sample data"""
    print("\n📋 Sample Data:")
    rwanda = Country.objects.get(name='Rwanda')
    provinces = Province.objects.filter(country=rwanda)
    
    for province in provinces[:2]:  # Show first 2 provinces
        print(f"\n{province.name}:")
        districts = District.objects.filter(province=province)[:3]
        for district in districts:
            print(f"  └─ {district.name}")
            sectors = Sector.objects.filter(district=district)[:2]
            for sector in sectors:
                print(f"      └─ {sector.name}")
                cells = Cell.objects.filter(sector=sector)[:1]
                for cell in cells:
                    print(f"          └─ {cell.name}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_hierarchical_data.py <sql_file>")
        sys.exit(1)
    
    import_data(sys.argv[1])
    show_sample()
