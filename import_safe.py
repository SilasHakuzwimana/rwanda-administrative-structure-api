#!/usr/bin/env python3
import os
import django
import re
import sys
import time
from django.db import transaction
from django.db import connections

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_admin_api.settings')
django.setup()

from location.models import Country, Province, District, Sector, Cell, Village

def parse_sql_file(sql_file):
    """Extract data from SQL file"""
    print("📖 Parsing SQL file...")
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {}
    tables = ['countries', 'provinces', 'districts', 'sectors', 'cells', 'villages']
    
    for table in tables:
        pattern = rf"INSERT INTO `{table}` \(.*?\) VALUES\s+(.*?);"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        records = []
        for match in matches:
            rows = re.findall(r'\(([^)]+)\)', match)
            for row in rows:
                values = [v.strip().strip("'") for v in row.split(',')]
                if values and len(values) >= 2:
                    records.append({
                        'id': int(values[0]) if values[0].isdigit() else None,
                        'name': values[1] if len(values) > 1 and values[1] != 'NULL' else None,
                        'parent_id': int(values[2]) if len(values) > 2 and values[2].isdigit() else None
                    })
        
        data[table] = records
        print(f"  ✓ {table}: {len(records)} records")
    
    return data

def safe_bulk_create(model, objects, batch_size=100, retries=3):
    """Safely bulk create with retry logic"""
    if not objects:
        return 0
    
    for attempt in range(retries):
        try:
            model.objects.bulk_create(objects, ignore_conflicts=True, batch_size=batch_size)
            connections['default'].close()  # Close connection to free up resources
            return len(objects)
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retry
                connections['default'].close()
            else:
                # Try one by one
                print(f"  Falling back to single inserts...")
                count = 0
                for obj in objects:
                    try:
                        obj.save()
                        count += 1
                        if count % 100 == 0:
                            print(f"    Saved {count} objects")
                    except Exception as save_error:
                        print(f"    Failed to save {obj}: {save_error}")
                return count
    return 0

def import_data_safe(sql_file):
    """Import data with safe batching"""
    
    print("\n🚀 Starting safe import to Aiven PostgreSQL...")
    print("="*50)
    
    # Parse SQL file
    data = parse_sql_file(sql_file)
    
    # Create Rwanda country
    rwanda, created = Country.objects.get_or_create(name='Rwanda')
    print(f"✓ Country: {rwanda.name}")
    
    # Import provinces
    print("\n📥 Importing provinces...")
    provinces_to_create = []
    existing_provinces = set(Province.objects.filter(country=rwanda).values_list('name', flat=True))
    
    for record in data['provinces']:
        if record['name'] and record['name'] not in existing_provinces:
            provinces_to_create.append(Province(name=record['name'], country=rwanda))
    
    if provinces_to_create:
        count = safe_bulk_create(Province, provinces_to_create, batch_size=50)
        print(f"  ✓ Added {count} provinces")
    else:
        print(f"  ✓ {len(Province.objects.filter(country=rwanda))} provinces already exist")
    
    # Create province mapping
    province_map = {p.name: p for p in Province.objects.filter(country=rwanda)}
    
    # Import districts in batches
    print("\n📥 Importing districts...")
    districts_to_create = []
    
    for record in data['districts']:
        if record['name'] and record['parent_id']:
            province_record = next((p for p in data['provinces'] if p['id'] == record['parent_id']), None)
            if province_record and province_record['name'] in province_map:
                province = province_map[province_record['name']]
                if not District.objects.filter(name=record['name'], province=province).exists():
                    districts_to_create.append(District(name=record['name'], province=province))
                
                if len(districts_to_create) >= 100:
                    count = safe_bulk_create(District, districts_to_create, batch_size=50)
                    print(f"  ✓ Added {count} districts (batch)")
                    districts_to_create = []
    
    if districts_to_create:
        count = safe_bulk_create(District, districts_to_create, batch_size=50)
        print(f"  ✓ Added {count} districts")
    
    print(f"✅ Total districts: {District.objects.count()}")
    
    # Import sectors in smaller batches
    print("\n📥 Importing sectors (this may take a few minutes)...")
    sectors_to_create = []
    
    for i, record in enumerate(data['sectors']):
        if record['name'] and record['parent_id']:
            district_record = next((d for d in data['districts'] if d['id'] == record['parent_id']), None)
            if district_record:
                province_record = next((p for p in data['provinces'] if p['id'] == district_record['parent_id']), None)
                if province_record and province_record['name'] in province_map:
                    province = province_map[province_record['name']]
                    district = District.objects.filter(name=district_record['name'], province=province).first()
                    if district and not Sector.objects.filter(name=record['name'], district=district).exists():
                        sectors_to_create.append(Sector(name=record['name'], district=district))
                        
                        if len(sectors_to_create) >= 50:
                            count = safe_bulk_create(Sector, sectors_to_create, batch_size=50)
                            print(f"  ✓ Added {count} sectors (batch {i//50 + 1})")
                            sectors_to_create = []
        
        if (i + 1) % 200 == 0:
            print(f"  Progress: {i+1}/{len(data['sectors'])} sectors processed")
    
    if sectors_to_create:
        count = safe_bulk_create(Sector, sectors_to_create, batch_size=50)
        print(f"  ✓ Added {count} sectors")
    
    print(f"✅ Total sectors: {Sector.objects.count()}")
    
    # Import cells in smaller batches
    print("\n📥 Importing cells...")
    cells_to_create = []
    
    for i, record in enumerate(data['cells']):
        if record['name'] and record['parent_id']:
            sector_record = next((s for s in data['sectors'] if s['id'] == record['parent_id']), None)
            if sector_record:
                district_record = next((d for d in data['districts'] if d['id'] == sector_record['parent_id']), None)
                if district_record:
                    province_record = next((p for p in data['provinces'] if p['id'] == district_record['parent_id']), None)
                    if province_record and province_record['name'] in province_map:
                        province = province_map[province_record['name']]
                        district = District.objects.filter(name=district_record['name'], province=province).first()
                        if district:
                            sector = Sector.objects.filter(name=sector_record['name'], district=district).first()
                            if sector and not Cell.objects.filter(name=record['name'], sector=sector).exists():
                                cells_to_create.append(Cell(name=record['name'], sector=sector))
                                
                                if len(cells_to_create) >= 100:
                                    count = safe_bulk_create(Cell, cells_to_create, batch_size=50)
                                    print(f"  ✓ Added {count} cells (batch)")
                                    cells_to_create = []
        
        if (i + 1) % 500 == 0:
            print(f"  Progress: {i+1}/{len(data['cells'])} cells processed")
    
    if cells_to_create:
        count = safe_bulk_create(Cell, cells_to_create, batch_size=50)
        print(f"  ✓ Added {count} cells")
    
    print(f"✅ Total cells: {Cell.objects.count()}")
    
    # Import villages in very small batches
    print("\n📥 Importing villages (this will take time, please wait)...")
    villages_to_create = []
    
    for i, record in enumerate(data['villages']):
        if record['name'] and record['parent_id']:
            cell_record = next((c for c in data['cells'] if c['id'] == record['parent_id']), None)
            if cell_record:
                sector_record = next((s for s in data['sectors'] if s['id'] == cell_record['parent_id']), None)
                if sector_record:
                    district_record = next((d for d in data['districts'] if d['id'] == sector_record['parent_id']), None)
                    if district_record:
                        province_record = next((p for p in data['provinces'] if p['id'] == district_record['parent_id']), None)
                        if province_record and province_record['name'] in province_map:
                            province = province_map[province_record['name']]
                            district = District.objects.filter(name=district_record['name'], province=province).first()
                            if district:
                                sector = Sector.objects.filter(name=sector_record['name'], district=district).first()
                                if sector:
                                    cell = Cell.objects.filter(name=cell_record['name'], sector=sector).first()
                                    if cell and not Village.objects.filter(name=record['name'], cell=cell).exists():
                                        villages_to_create.append(Village(name=record['name'], cell=cell))
                                        
                                        if len(villages_to_create) >= 200:
                                            count = safe_bulk_create(Village, villages_to_create, batch_size=100)
                                            print(f"  ✓ Added {count} villages (batch {i//200 + 1})")
                                            villages_to_create = []
                                            time.sleep(1)  # Small pause to prevent connection issues
        
        if (i + 1) % 2000 == 0:
            print(f"  Progress: {i+1}/{len(data['villages'])} villages processed")
            connections['default'].close()  # Refresh connection
    
    if villages_to_create:
        count = safe_bulk_create(Village, villages_to_create, batch_size=100)
        print(f"  ✓ Added {count} villages")
    
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_safe.py <sql_file>")
        sys.exit(1)
    
    try:
        result = import_data_safe(sys.argv[1])
        if result:
            print("\n🎉 Import completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️ Import interrupted by user")
        print("You can resume by running the script again - it will skip existing records")
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        print("\nTry running again - the script will skip already imported records")
