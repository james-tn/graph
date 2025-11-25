from pathlib import Path

root_out = Path('output')
data_out = Path('data/output')

print(f"Root output exists: {root_out.exists()}")
print(f"Data output exists: {data_out.exists()}")
print(f"Data output/lancedb exists: {(data_out / 'lancedb').exists()}")

if data_out.exists():
    items = list(data_out.iterdir())
    print(f"\nItems in data/output: {[item.name for item in items]}")
    
    if (data_out / 'lancedb').exists():
        lance_items = list((data_out / 'lancedb').iterdir())
        print(f"Items in data/output/lancedb: {[item.name for item in lance_items]}")
