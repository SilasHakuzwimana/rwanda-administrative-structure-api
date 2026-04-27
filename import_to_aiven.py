#!/usr/bin/env python3
import os
import django
import re
import sys
from django.db import transaction
from django.db import IntegrityError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_admin_api.settings')
django.setup()

from location.models import Country, Province, District, Sector, Cell, Village

def parse_sql_file(sql_file):
    """Extract data from SQL file efficiently"""
    print("📖 Parsing SQL file...")
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {}
    tables = ['countries', 'provinces', 'districts', 'sectors', 'cells', 'villages']
    
    for table in tables:
        # Find INSERT statements
        pattern = rf"INSERT INTO `{table}` \(.*?\) VALUES\s+(.*?);"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        records = []
        for match in matches:
            # Parse values - simplified approach
            # Replace )), with ); to split rows
            rows = re.findall(r'\(([^)]+)\)', match)
            for row in rows:
                # Simple split on comma
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

@transaction.atomic
def import_data_optimized(sql_file):
    """Optimized import using bulk operations"""
    
    print("\n🚀 Starting optimized import to Aiven PostgreSQL...")
    print("="*50)
    
    # Parse SQL file
    data = parse_sql_file(sql_file)
    
    # Create Rwanda country
    rwanda, created = Country.objects.get_or_create(name='Rwanda')
    print(f"✓ Country: {rwanda.name}")
    
    # Import provinces (bulk create)
    print("\n📥 Importing provinces...")
    provinces_to_create = []
    existing_provinces = set(Province.objects.filter(country=rwanda).values_list('name', flat=True))
    
    for record in data['provinces']:
        if record['name'] and record['name'] not in existing_provinces:
            provinces_to_create.append(Province(name=record['name'], country=rwanda))
    
    if provinces_to_create:
        Province.objects.bulk_create(provinces_to_create, ignore_conflicts=True)
        print(f"  ✓ Added {len(provinces_to_create)} provinces")
    
    # Create mapping
    province_map = {p.name: p for p in Province.objects.filter(country=rwanda)}
    print(f"✅ Total provinces: {len(province_map)}")
    
    # Import districts (bulk)
    print("\n📥 Importing districts...")
    districts_to_create = []
    existing_districts = set(District.objects.values_list('name', 'province_id'))
    
    for record in data['districts']:
        if record['name'] and record['parent_id']:
            # Find province by matching with data
            province_record = next((p for p in data['provinces'] if p['id'] == record['parent_id']), None)
            if province_record and province_record['name'] in province_map:
                province = province_map[province_record['name']]
                if (record['name'], province.id) not in existing_districts:
                    districts_to_create.append(District(name=record['name'], province=province))
                    
                    if len(districts_to_create) % 50 == 0:
                        print(f"  ...processed {len(districts_to_create)} districts")
    
    if districts_to_create:
        District.objects.bulk_create(districts_to_create, ignore_conflicts=True, batch_size=500)
        print(f"  ✓ Added {len(districts_to_create)} districts")
    
    # Create district mapping
    district_map = {(d.name, d.province_id): d for d in District.objects.all()}
    print(f"✅ Total districts: {len(district_map)}")
    
    # Import sectors (bulk)
    print("\n📥 Importing sectors...")
    sectors_to_create = []
    existing_sectors = set(Sector.objects.values_list('name', 'district_id'))
    
    for i, record in enumerate(data['sectors']):
        if record['name'] and record['parent_id']:
            # Find district
            district_record = next((d for d in data['districts'] if d['id'] == record['parent_id']), None)
            if district_record:
                # Find province for this district
                province_record = next((p for p in data['provinces'] if p['id'] == district_record['parent_id']), None)
                if province_record and province_record['name'] in province_map:
                    province = province_map[province_record['name']]
                    district = District.objects.filter(name=district_record['name'], province=province).first()
                    if district and (record['name'], district.id) not in existing_sectors:
                        sectors_to_create.append(Sector(name=record['name'], district=district))
                        
                        if len(sectors_to_create) % 100 == 0:
                            print(f"  ...processed {len(sectors_to_create)} sectors")
        
        # Show progress
        if (i + 1) % 500 == 0:
            print(f"  Progress: {i+1}/{len(data['sectors'])} sectors processed")
    
    if sectors_to_create:
        Sector.objects.bulk_create(sectors_to_create, ignore_conflicts=True, batch_size=500)
        print(f"  ✓ Added {len(sectors_to_create)} sectors")
    
    # Create sector mapping
    sector_map = {(s.name, s.district_id): s for s in Sector.objects.all()}
    print(f"✅ Total sectors: {len(sector_map)}")
    
    # Import cells (bulk)
    print("\n📥 Importing cells...")
    cells_to_create = []
    existing_cells = set(Cell.objects.values_list('name', 'sector_id'))
    
    for i, record in enumerate(data['cells']):
        if record['name'] and record['parent_id']:
            sector_record = next((s for s in data['sectors'] if s['id'] == record['parent_id']), None)
            if sector_record:
                # Find district and province
                district_record = next((d for d in data['districts'] if d['id'] == sector_record['parent_id']), None)
                if district_record:
                    province_record = next((p for p in data['provinces'] if p['id'] == district_record['parent_id']), None)
                    if province_record and province_record['name'] in province_map:
                        province = province_map[province_record['name']]
                        district = District.objects.filter(name=district_record['name'], province=province).first()
                        if district:
                            sector = Sector.objects.filter(name=sector_record['name'], district=district).first()
                            if sector and (record['name'], sector.id) not in existing_cells:
                                cells_to_create.append(Cell(name=record['name'], sector=sector))
                                
                                if len(cells_to_create) % 200 == 0:
                                    print(f"  ...processed {len(cells_to_create)} cells")
        
        if (i + 1) % 500 == 0:
            print(f"  Progress: {i+1}/{len(data['cells'])} cells processed")
    
    if cells_to_create:
        Cell.objects.bulk_create(cells_to_create, ignore_conflicts=True, batch_size=500)
        print(f"  ✓ Added {len(cells_to_create)} cells")
    
    # Create cell mapping
    cell_map = {(c.name, c.sector_id): c for c in Cell.objects.all()}
    print(f"✅ Total cells: {len(cell_map)}")
    
    # Import villages (bulk)
    print("\n📥 Importing villages...")
    villages_to_create = []
    existing_villages = set(Village.objects.values_list('name', 'cell_id'))
    
    for i, record in enumerate(data['villages']):
        if record['name'] and record['parent_id']:
            cell_record = next((c for c in data['cells'] if c['id'] == record['parent_id']), None)
            if cell_record:
                # Find the full hierarchy
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
                                    if cell and (record['name'], cell.id) not in existing_villages:
                                        villages_to_create.append(Village(name=record['name'], cell=cell))
                                        
                                        if len(villages_to_create) % 500 == 0:
                                            print(f"  ...processed {len(villages_to_create)} villages")
        
        if (i + 1) % 2000 == 0:
            print(f"  Progress: {i+1}/{len(data['villages'])} villages processed")
    
    if villages_to_create:
        Village.objects.bulk_create(villages_to_create, ignore_conflicts=True, batch_size=1000)
        print(f"  ✓ Added {len(villages_to_create)} villages")
    
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
        print("Usage: python import_optimized.py <sql_file>")
        sys.exit(1)
    
    result = import_data_optimized(sys.argv[1])
    
    if result:
        print("\n🎉 Import completed successfully!")
    else:
        print("\n❌ Import failed!")