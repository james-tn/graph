import lancedb
import pandas as pd

# Connect to LanceDB
db = lancedb.connect('data/output/lancedb')

# List all tables
table_names = db.table_names()
print(f"Tables: {table_names}\n")

# Check each table structure
for table_name in table_names:
    print(f"\n{'='*60}")
    print(f"Table: {table_name}")
    print('='*60)
    
    tbl = db.open_table(table_name)
    df = tbl.to_pandas()
    
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst row:")
    if len(df) > 0:
        print(df.head(1).to_dict(orient='records')[0])
