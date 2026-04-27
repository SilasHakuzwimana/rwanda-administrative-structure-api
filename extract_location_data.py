import re

def extract_location_data(input_file, output_file):
    """Extract only location tables from MySQL dump"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tables we want
    location_tables = ['countries', 'provinces', 'districts', 'sectors', 'cells', 'villages']
    
    extracted = []
    
    for table in location_tables:
        # Extract CREATE TABLE
        create_pattern = rf'CREATE TABLE `{table}` \((.*?)\);'
        create_match = re.search(create_pattern, content, re.DOTALL | re.IGNORECASE)
        if create_match:
            extracted.append(f'-- Table structure for table `{table}`')
            extracted.append(f'CREATE TABLE "{table}" ({create_match.group(1)});')
            extracted.append('')
        
        # Extract INSERT statements
        insert_pattern = rf'INSERT INTO `{table}` \([^)]+\) VALUES(.*?);'
        insert_matches = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if insert_matches:
            extracted.append(f'-- Dumping data for table `{table}`')
            for insert in insert_matches:
                extracted.append(f'INSERT INTO "{table}" VALUES{insert};')
            extracted.append('')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(extracted))
    
    print(f"✅ Extracted location data to {output_file}")

# Extract the data
extract_location_data('if0_36150530_rwanda_data_db.sql', 'location_data.sql')
print("Extraction complete!")
