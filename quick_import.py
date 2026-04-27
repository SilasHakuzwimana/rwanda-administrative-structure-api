import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

# Read and execute SQL directly
with open('if0_36150530_rwanda_data_db.sql', 'r') as f:
    sql = f.read()
    
    # Split into individual statements
    statements = sql.split(';')
    
    for stmt in statements:
        if stmt.strip():
            try:
                cur.execute(stmt)
                print("✓ Executed statement")
            except Exception as e:
                print(f"Error: {e}")
    
conn.commit()
print("Import complete!")

