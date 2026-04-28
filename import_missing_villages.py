#!/usr/bin/env python3
import os
import django
import re
import sys
from django.db import connections

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_admin_api.settings')
django.setup()

from location.models import Country, Province, District, Sector, Cell, Village

def parse_all_data(sql_file):
    """Parse all location data from SQL file"""
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
                if len(values) >= 2:
                    records.append({
                        'id': int(values[0]) if values[0].isdigit() else None,
                        'name': values[1] if len(values) > 1 and values[1] != 'NULL' else None,
                        'parent_id': int(values[2]) if len(values) > 2 and values[2].isdigit() else None
                    })
        
        data[table] = records
        print(f"  ✓ {table}: {len(records)} records")
    
    return data

def build_hierarchy_mapping(data):
    """Build mapping from SQL IDs to database objects using names"""
    
    print("\n📊 Building hierarchy mapping...")
    
    # Get all database objects
    countries = {c.name: c for c in Country.objects.all()}
    provinces = {p.name: p for p in Province.objects.all()}
    districts = {(d.name, d.province_id): d for d in District.objects.all()}
    sectors = {(s.name, s.district_id): s for s in Sector.objects.all()}
    cells = {(c.name, c.sector_id): c for c in Cell.objects.all()}
    
    # Build SQL name->ID mapping
    sql_countries = {rec['id']: rec['name'] for rec in data['countries']}
    sql_provinces = {rec['id']: rec['name'] for rec in data['provinces']}
    sql_districts = {}
    sql_sectors = {}
    sql_cells = {}
    
    for rec in data['districts']:
        if rec['id'] and rec['parent_id']:
            province_name = sql_provinces.get(rec['parent_id'])
            if province_name:
                sql_districts[rec['id']] = {
                    'name': rec['name'],
                    'province_name': province_name
                }
    
    for rec in data['sectors']:
        if rec['id'] and rec['parent_id']:
            district_info = sql_districts.get(rec['parent_id'])
            if district_info:
                sql_sectors[rec['id']] = {
                    'name': rec['name'],
                    'district_name': district_info['name'],
                    'province_name': district_info['province_name']
                }
    
    for rec in data['cells']:
        if rec['id'] and rec['parent_id']:
            sector_info = sql_sectors.get(rec['parent_id'])
            if sector_info:
                sql_cells[rec['id']] = {
                    'name': rec['name'],
                    'sector_name': sector_info['name'],
                    'district_name': sector_info['district_name'],
                    'province_name': sector_info['province_name']
                }
    
    # Map SQL cell IDs to database cell objects
    cell_id_map = {}
    for sql_id, cell_info in sql_cells.items():
        province = provinces.get(cell_info['province_name'])
        if province:
            district = districts.get((cell_info['district_name'], province.id))
            if district:
                sector = sectors.get((cell_info['sector_name'], district.id))
                if sector:
                    db_cell = cells.get((cell_info['name'], sector.id))
                    if db_cell:
                        cell_id_map[sql_id] = db_cell
    
    print(f"  ✓ Mapped {len(cell_id_map)} cells")
    
    return cell_id_map

def import_missing_villages(sql_file):
    """Import only missing villages by matching cell names"""
    
    print("\n🚀 Importing missing villages to Aiven PostgreSQL...")
    print("="*50)
    
    # Parse SQL data
    data = parse_all_data(sql_file)
    
    # Build cell mapping
    cell_id_map = build_hierarchy_mapping(data)
    
    # Get existing villages
    existing_villages = set()
    for village in Village.objects.select_related('cell').all():
        existing_villages.add((village.name, village.cell_id))
    
    print(f"\n📊 Current villages: {len(existing_villages)}")
    print(f"📊 Total villages in SQL: {len(data['villages'])}")
    
    # Find and import missing villages
    missing_villages = []
    for village in data['villages']:
        if not village['name'] or not village['parent_id']:
            continue
        
        cell = cell_id_map.get(village['parent_id'])
        if cell and (village['name'], cell.id) not in existing_villages:
            missing_villages.append(Village(name=village['name'], cell=cell))
    
    print(f"📊 Missing villages to import: {len(missing_villages)}")
    
    if not missing_villages:
        print("✅ All villages already imported!")
        return True
    
    # Import in batches
    print("\n📥 Importing villages in batches...")
    batch_size = 500
    imported = 0
    
    for i in range(0, len(missing_villages), batch_size):
        batch = missing_villages[i:i+batch_size]
        try:
            Village.objects.bulk_create(batch, ignore_conflicts=True, batch_size=batch_size)
            imported += len(batch)
            print(f"  ✓ Batch {i//batch_size + 1}: Imported {len(batch)} villages (Total: {imported}/{len(missing_villages)})")
            
            # Refresh connection periodically
            if (i // batch_size) % 5 == 0:
                connections['default'].close()
                
        except Exception as e:
            print(f"  ⚠️ Batch failed: {e}")
            # Try one by one
            for village in batch:
                try:
                    village.save()
                    imported += 1
                except Exception as single_error:
                    print(f"    ❌ Failed: {village.name} - {single_error}")
    
    # Final statistics
    final_count = Village.objects.count()
    print("\n" + "="*50)
    print("📊 FINAL STATISTICS")
    print("="*50)
    print(f"Villages before: {len(existing_villages)}")
    print(f"Villages imported: {imported}")
    print(f"Villages now: {final_count}")
    print(f"Target: 14,840")
    
    if final_count == 14840:
        print("\n🎉 All 14,840 villages imported successfully!")
    else:
        remaining = 14840 - final_count
        print(f"\n⚠️ {remaining} villages remaining to import")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_missing_villages.py <sql_file>")
        sys.exit(1)
    
    try:
        import_missing_villages(sys.argv[1])
    except KeyboardInterrupt:
        print("\n\n⚠️ Import interrupted by user")
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
