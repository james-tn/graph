"""Check relationship types in the database."""
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

# Database configuration (same as other scripts)
DB_HOST = os.environ.get("POSTGRES_HOST", "ci-ci-dev-pgflex.postgres.database.azure.com")
DB_NAME = os.environ.get("POSTGRES_DATABASE", "cipgraph")
DB_USER = os.environ.get("POSTGRES_USER", "ciadmin")
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    sslmode='require'
)
cur = conn.cursor()

# Check if Apache AGE is installed
print("\n" + "=" * 70)
print("Checking Apache AGE Installation:")
print("=" * 70)
cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'age';")
age_result = cur.fetchone()
if age_result:
    print(f"  [OK] Apache AGE is installed: version {age_result[1]}")
    
    # Check if graph was created (without LOAD which requires superuser)
    try:
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        cur.execute("""
            SELECT name, namespace FROM ag_catalog.ag_graph WHERE name = 'contract_intelligence';
        """)
        graph_result = cur.fetchone()
        
        if graph_result:
            print(f"  ✓ Graph 'contract_intelligence' exists (namespace: {graph_result[1]})")
        else:
            print("  ✗ Graph 'contract_intelligence' does NOT exist!")
            print("\n  Apache AGE is installed but graph hasn't been created.")
            print("  Run build_graph.py to create and populate the graph.")
            conn.close()
            exit(0)
    except Exception as e:
        print(f"  Error checking graph: {e}")
        print("\n  Continuing with relationship check...")
else:
    print("  ✗ Apache AGE is NOT installed!")
    print("\n  This explains why Cypher queries don't work.")
    print("  The graph layer has never been created.")
    conn.close()
    exit(0)

# Check distinct relationship types
print("\n" + "=" * 70)
print("Relationship types in contract_relationships table:")
print("=" * 70)
cur.execute("SELECT DISTINCT relationship_type FROM contract_relationships ORDER BY relationship_type")
for row in cur.fetchall():
    print(f"  - {row[0]}")

# Check SOW relationships specifically
print("\n" + "=" * 70)
print("SOW Relationships (SQL):")
print("=" * 70)
cur.execute("""
    SELECT 
        child.contract_identifier as sow_identifier,
        child.title as sow_title,
        parent.contract_identifier as parent_identifier,
        parent.title as parent_title,
        cr.relationship_type
    FROM contract_relationships cr
    JOIN contracts child ON cr.child_contract_id = child.id
    JOIN contracts parent ON cr.parent_contract_id = parent.id
    WHERE cr.relationship_type ILIKE '%sow%'
    ORDER BY parent.contract_identifier
    LIMIT 10
""")

rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"\n  SOW: {row[0]}")
        print(f"    Title: {row[1]}")
        print(f"    Parent: {row[2]}")
        print(f"    Parent Title: {row[3]}")
        print(f"    Relationship Type: '{row[4]}'")
else:
    print("  No SOW relationships found")

# Check what contract relationship edges exist in the graph
print("\n" + "=" * 70)
print("All contract relationship edges in graph:")
print("=" * 70)

conn.commit()  # Clear any transaction errors

for rel_type in ['SOW_OF', 'WORK_ORDER_OF', 'AMENDS', 'ADDENDUM_TO', 'MAINTENANCE_OF', 'RELATED_TO']:
    try:
        cur.execute(f"""
            SELECT * FROM ag_catalog.cypher('contract_intelligence', $$
                MATCH ()-[r:{rel_type}]->()
                RETURN count(r) as count
            $$) as (count agtype);
        """)
        result = cur.fetchone()
        count = int(str(result[0])) if result and result[0] else 0
        print(f"  {rel_type}: {count}")
        conn.commit()
    except Exception as e:
        print(f"  {rel_type}: Error - {e}")
        conn.rollback()

# Try to find ANY relationships between contracts
print("\n" + "=" * 70)
print("Sample of ANY relationships between Contract nodes:")
print("=" * 70)
try:
    cur.execute("""
        SELECT * FROM ag_catalog.cypher('contract_intelligence', $$
            MATCH (c1:Contract)-[r]->(c2:Contract)
            RETURN count(r) as count
        $$) as (count agtype);
    """)
    result = cur.fetchone()
    count = int(str(result[0])) if result and result[0] else 0
    print(f"  Total Contract-to-Contract relationships: {count}")
    
    if count > 0:
        cur.execute("""
            SELECT * FROM ag_catalog.cypher('contract_intelligence', $$
                MATCH (c1:Contract)-[r]->(c2:Contract)
                RETURN c1.identifier, type(r), c2.identifier
                LIMIT 5
            $$) as (child agtype, rel_type agtype, parent agtype);
        """)
        print("\n  First 5 relationships:")
        for row in cur.fetchall():
            child = str(row[0]).strip('"')
            rel = str(row[1]).strip('"')
            parent = str(row[2]).strip('"')
            print(f"    {child} -[{rel}]-> {parent}")
    conn.commit()
except Exception as e:
    print(f"  Error: {e}")
    conn.rollback()

# Now test the agent's actual query pattern
print("\n" + "=" * 70)
print("Testing Agent's Query Pattern (as provided):")
print("=" * 70)
try:
    cur.execute("""
        SELECT * FROM ag_catalog.cypher('contract_intelligence', $$
            MATCH (msa:Contract)-[:SOW_OF]->(sow:Contract)
            WHERE msa.type = 'Master Services Agreement'
              AND sow.type = 'Statement of Work'
              AND sow.status = 'active'
            RETURN msa.identifier, msa.type, sow.identifier, sow.type, sow.status
            LIMIT 10
        $$) as (msa_id agtype, msa_type agtype, sow_id agtype, sow_type agtype, sow_status agtype);
    """)
    results = cur.fetchall()
    print(f"  Results found: {len(results)}")
    if results:
        for row in results:
            msa_id = str(row[0]).strip('"')
            msa_type = str(row[1]).strip('"')
            sow_id = str(row[2]).strip('"')
            sow_type = str(row[3]).strip('"')
            sow_status = str(row[4]).strip('"')
            print(f"    MSA: {msa_id} ({msa_type})")
            print(f"    SOW: {sow_id} ({sow_type}, status: {sow_status})")
    else:
        print("  No results - investigating why...")
        
    conn.commit()
except Exception as e:
    print(f"  Error: {e}")
    conn.rollback()

# Check what actual values exist in the graph
print("\n" + "=" * 70)
print("Checking actual SOW_OF relationships (no filters):")
print("=" * 70)
try:
    cur.execute("""
        SELECT * FROM ag_catalog.cypher('contract_intelligence', $$
            MATCH (child:Contract)-[:SOW_OF]->(parent:Contract)
            RETURN child.identifier, child.type, child.status, parent.identifier, parent.type
            LIMIT 5
        $$) as (child_id agtype, child_type agtype, child_status agtype, parent_id agtype, parent_type agtype);
    """)
    results = cur.fetchall()
    print(f"  Found {len(results)} SOW_OF relationships:")
    for row in results:
        child_id = str(row[0]).strip('"') if row[0] else 'NULL'
        child_type = str(row[1]).strip('"') if row[1] else 'NULL'
        child_status = str(row[2]).strip('"') if row[2] else 'NULL'
        parent_id = str(row[3]).strip('"') if row[3] else 'NULL'
        parent_type = str(row[4]).strip('"') if row[4] else 'NULL'
        print(f"    {child_id} (type: {child_type}, status: {child_status})")
        print(f"      -> {parent_id} (type: {parent_type})")
        print()
    conn.commit()
except Exception as e:
    print(f"  Error: {e}")
    conn.rollback()
except Exception as e:
    print(f"  Error: {e}")
    conn.rollback()

cur.close()
conn.close()
