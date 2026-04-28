#!/usr/bin/env python3
import os
import django
import re
import sys
import time
from django.db import connections
from django.db import IntegrityError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_admin_api.settings')
django.setup()

from location.models import Country, Province, District, Sector, Cell, Village

def parse_villages_only(sql_file):
    """Extract only village data from SQL file"""
    print("📖 Parsing village data from SQL file...")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find village INSERT statements
    pattern = r"INSERT INTO `villages` \(.*?\) VALUES\s+(.*?);"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    villages = []
    for match in matches:
        # Parse each value row
        rows = re.findall(r'\(([^)]+)\)', match)
        for row in rows:
            values = [v.strip().strip("'") for v in row.split(',')]
            if len(values) >= 3:
                villages.append({
                    'id': int(values[0]) if values[0].isdigit() else None,
                    'name': values[1] if values[1] != 'NULL' else None,
                    'cell_id': int(values[2]) if values[2].isdigit() else None
                })
    
    print(f"  ✓ Found {len(villages)} total villages in SQL")
    return villages

def get_existing_villages():
    """Get set of existing village names by cell"""
    existing = set()
    for village in Village.objects.select_related('cell').all():
        existing.add((village.name, village.cell_id))
    return existing

def import_remaining_villages(sql_file):
    """Import only missing villages"""
    
    print("\n🚀 Importing remaining villages to Aiven PostgreSQL...")
    print("="*50)
    
    # Get existing villages
    print("📊 Checking existing villages...")
    existing_villages = get_existing_villages()
    print(f"  ✓ Existing villages: {len(existing_villages)}")
    
    # Parse villages from SQL
    all_villages = parse_villages_only(sql_file)
    print(f"  ✓ Total villages in SQL: {len(all_villages)}")
    
    # Create mapping of cell_id to cell objects
    print("📊 Building cell mapping...")
    cell_cache = {}
    cells = Cell.objects.select_related('sector__district__province__country').all()
    for cell in cells:
        cell_cache[cell.id] = cell
    print(f"  ✓ Found {len(cell_cache)} cells")
    
    # Find missing villages
    print("🔍 Finding missing villages...")
    missing_villages = []
    for village_data in all_villages:
        if not village_data['name']:
            continue
            
        cell_id = village_data['cell_id']
        if cell_id and cell_id in cell_cache:
            if (village_data['name'], cell_id) not in existing_villages:
                missing_villages.append({
                    'name': village_data['name'],
                    'cell': cell_cache[cell_id]
                })
    
    print(f"  ✓ Missing villages to import: {len(missing_villages)}")
    
    if len(missing_villages) == 0:
        print("\n✅ All villages already imported!")
        return True
    
    # Import in small batches
    print("\n📥 Importing missing villages in batches...")
    batch_size = 200
    imported = 0
    failed = 0
    
    for i in range(0, len(missing_villages), batch_size):
        batch = missing_villages[i:i+batch_size]
        villages_to_create = []
        
        for village_data in batch:
            villages_to_create.append(
                Village(name=village_data['name'], cell=village_data['cell'])
            )
        
        try:
            # Try bulk create
            Village.objects.bulk_create(villages_to_create, ignore_conflicts=True, batch_size=batch_size)
            imported += len(villages_to_create)
            print(f"  ✓ Batch {i//batch_size + 1}: Imported {len(villages_to_create)} villages (Total: {imported})")
            
            # Refresh connection periodically
            if (i // batch_size) % 5 == 0:
                connections['default'].close()
                time.sleep(0.5)
                
        except Exception as e:
            print(f"  ⚠️ Batch failed: {e}")
            # Try one by one
            for village_data in batch:
                try:
                    Village.objects.create(name=village_data['name'], cell=village_data['cell'])
                    imported += 1
                except Exception as single_error:
                    failed += 1
                    if failed <= 10:
                        print(f"    ❌ Failed: {village_data['name']} - {single_error}")
        
        # Show progress
        progress = (i + len(batch)) / len(missing_villages) * 100
        print(f"  Progress: {min(progress, 100):.1f}% ({imported+failed}/{len(missing_villages)})")
    
    # Final statistics
    print("\n" + "="*50)
    print("📊 FINAL STATISTICS")
    print("="*50)
    print(f"Total villages in SQL: {len(all_villages)}")
    print(f"Previously imported: {len(existing_villages)}")
    print(f"Newly imported: {imported}")
    print(f"Failed: {failed}")
    print(f"Current total in Aiven: {Village.objects.count()}")
    print("="*50)
    
    if imported > 0:
        print("\n🎉 Successfully imported remaining villages!")
    else:
        print("\n⚠️ No new villages were imported")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_remaining_villages.py <sql_file>")
        sys.exit(1)
    
    try:
        result = import_remaining_villages(sys.argv[1])
    except KeyboardInterrupt:
        print("\n\n⚠️ Import interrupted by user")
        print("Run again to continue importing remaining villages")
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify Aiven PostgreSQL is accessible")
        print("3. Run: python manage.py check")
