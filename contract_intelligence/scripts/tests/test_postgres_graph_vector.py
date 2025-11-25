#!/usr/bin/env python3
"""
Test script for PostgreSQL vector and graph search capabilities.
Tests pgvector extension and Apache AGE graph queries.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

# Connection parameters
DB_HOST = "ci-ci-dev-pgflex.postgres.database.azure.com"
DB_NAME = "cipgraph"
DB_USER = "pgadmin"
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")

if not DB_PASSWORD:
    print("ERROR: POSTGRES_ADMIN_PASSWORD environment variable not set")
    exit(1)


def get_connection():
    """Create a database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )


def test_basic_connection():
    """Test basic database connectivity."""
    print("\n=== Testing Basic Connection ===")
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✓ Connected to PostgreSQL")
        print(f"  Version: {version[:50]}...")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_extensions():
    """Check installed extensions."""
    print("\n=== Checking Extensions ===")
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check available extensions
        cur.execute("""
            SELECT name, installed_version, default_version, comment
            FROM pg_available_extensions
            WHERE name IN ('vector', 'age', 'pg_trgm', 'hstore', 'citext')
            ORDER BY name;
        """)
        extensions = cur.fetchall()
        
        print(f"Found {len(extensions)} extensions:")
        for ext in extensions:
            status = "✓ INSTALLED" if ext['installed_version'] else "○ Available"
            print(f"  {status}: {ext['name']} - {ext['comment'][:60]}...")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Extension check failed: {e}")
        return False


def test_vector_search():
    """Test pgvector extension with vector similarity search."""
    print("\n=== Testing Vector Search (pgvector) ===")
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Create vector extension if not exists
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✓ Vector extension enabled")
        
        # Create test table
        cur.execute("DROP TABLE IF EXISTS test_embeddings;")
        cur.execute("""
            CREATE TABLE test_embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(384)
            );
        """)
        print("✓ Created test table with vector column (384 dimensions)")
        
        # Insert sample vectors
        sample_data = [
            ("Document about AI and machine learning", np.random.rand(384).tolist()),
            ("Article on database optimization", np.random.rand(384).tolist()),
            ("Guide to graph algorithms", np.random.rand(384).tolist()),
            ("Tutorial on vector databases", np.random.rand(384).tolist()),
            ("Introduction to PostgreSQL", np.random.rand(384).tolist()),
        ]
        
        for content, embedding in sample_data:
            cur.execute(
                "INSERT INTO test_embeddings (content, embedding) VALUES (%s, %s);",
                (content, embedding)
            )
        conn.commit()
        print(f"✓ Inserted {len(sample_data)} test documents")
        
        # Create vector index
        cur.execute("CREATE INDEX ON test_embeddings USING hnsw (embedding vector_cosine_ops);")
        conn.commit()
        print("✓ Created HNSW index for fast similarity search")
        
        # Perform similarity search
        query_vector = np.random.rand(384).tolist()
        cur.execute("""
            SELECT content, 1 - (embedding <=> %s::vector) AS similarity
            FROM test_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT 3;
        """, (query_vector, query_vector))
        
        results = cur.fetchall()
        print(f"\n✓ Vector similarity search results (top 3):")
        for i, (content, similarity) in enumerate(results, 1):
            print(f"  {i}. {content[:50]}... (similarity: {similarity:.4f})")
        
        # Cleanup
        cur.execute("DROP TABLE test_embeddings;")
        conn.commit()
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Vector search test failed: {e}")
        return False


def test_graph_search():
    """Test Apache AGE extension with graph queries."""
    print("\n=== Testing Graph Search (Apache AGE) ===")
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Create AGE extension if not exists
        cur.execute("CREATE EXTENSION IF NOT EXISTS age;")
        print("✓ AGE extension enabled")
        
        # Set search path to include AGE catalog (AGE is preloaded via shared_preload_libraries)
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Create a graph
        cur.execute("SELECT create_graph('test_graph');")
        conn.commit()
        print("✓ Created test graph")
        
        # Create nodes (people)
        people = [
            ("Alice", "Engineer"),
            ("Bob", "Manager"),
            ("Carol", "Designer"),
            ("Dave", "Engineer")
        ]
        
        print("✓ Creating nodes...")
        for name, role in people:
            cur.execute("""
                SELECT * FROM cypher('test_graph', $$
                    CREATE (p:Person {name: '%s', role: '%s'})
                    RETURN p
                $$) as (p agtype);
            """ % (name, role))
            conn.commit()
        
        # Create relationships
        relationships = [
            ("Alice", "Bob", "REPORTS_TO"),
            ("Dave", "Bob", "REPORTS_TO"),
            ("Carol", "Bob", "REPORTS_TO"),
            ("Alice", "Dave", "COLLABORATES_WITH"),
            ("Alice", "Carol", "COLLABORATES_WITH")
        ]
        
        print("✓ Creating relationships...")
        for from_name, to_name, rel_type in relationships:
            cur.execute("""
                SELECT * FROM cypher('test_graph', $$
                    MATCH (a:Person {name: '%s'}), (b:Person {name: '%s'})
                    CREATE (a)-[r:%s]->(b)
                    RETURN r
                $$) as (r agtype);
            """ % (from_name, to_name, rel_type))
            conn.commit()
        
        # Query: Find all people and their roles
        print("\n✓ Graph query results:")
        cur.execute("""
            SELECT * FROM cypher('test_graph', $$
                MATCH (p:Person)
                RETURN p.name, p.role
                ORDER BY p.name
            $$) as (name agtype, role agtype);
        """)
        results = cur.fetchall()
        print(f"  Found {len(results)} people:")
        for name, role in results:
            print(f"    • {name}: {role}")
        
        # Query: Find who reports to Bob
        cur.execute("""
            SELECT * FROM cypher('test_graph', $$
                MATCH (p:Person)-[:REPORTS_TO]->(m:Person {name: 'Bob'})
                RETURN p.name
                ORDER BY p.name
            $$) as (name agtype);
        """)
        results = cur.fetchall()
        print(f"\n  People reporting to Bob:")
        for (name,) in results:
            print(f"    • {name}")
        
        # Query: Find collaboration paths
        cur.execute("""
            SELECT * FROM cypher('test_graph', $$
                MATCH (p1:Person {name: 'Alice'})-[:COLLABORATES_WITH]-(p2:Person)
                RETURN p2.name
            $$) as (name agtype);
        """)
        results = cur.fetchall()
        print(f"\n  Alice collaborates with:")
        for (name,) in results:
            print(f"    • {name}")
        
        # Cleanup
        cur.execute("SELECT drop_graph('test_graph', true);")
        conn.commit()
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Graph search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PostgreSQL Graph & Vector Search Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Basic Connection", test_basic_connection()))
    results.append(("Extensions Check", test_extensions()))
    results.append(("Vector Search", test_vector_search()))
    results.append(("Graph Search", test_graph_search()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nPassed: {passed_count}/{total_count}")
    
    return all(passed for _, passed in results)


if __name__ == "__main__":
    exit(0 if main() else 1)
