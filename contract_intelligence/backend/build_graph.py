#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Apache AGE Graph Builder for Contract Intelligence

Creates graph nodes and relationships to enable multi-hop reasoning:
- Nodes: Contract, Party, Clause, Obligation, Right, Term
- Edges: IS_PARTY_TO, CONTAINS_CLAUSE, IMPOSES_OBLIGATION, GRANTS_RIGHT, DEFINES_TERM, etc.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration from environment variables
DB_HOST = os.environ.get("POSTGRES_HOST", "ci-ci-dev-pgflex.postgres.database.azure.com")
DB_NAME = os.environ.get("POSTGRES_DATABASE", "cipgraph")
DB_USER = os.environ.get("POSTGRES_USER", "pgadmin")
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")

GRAPH_NAME = "contract_intelligence"


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require',
        cursor_factory=RealDictCursor
    )


def execute_age_query(cur, query: str):
    """Execute Apache AGE Cypher query."""
    try:
        cur.execute(query)
        return cur.fetchall()
    except Exception as e:
        print(f"  ⚠ Query error: {e}")
        return []


def create_graph(cur, conn):
    """Initialize Apache AGE graph."""
    print("🔧 Creating AGE graph...")
    
    # Drop existing graph if it exists
    try:
        execute_age_query(cur, f"SELECT drop_graph('{GRAPH_NAME}', true);")
        conn.commit()
        print("  ✓ Dropped existing graph")
    except:
        pass
    
    # Create new graph
    execute_age_query(cur, f"SELECT create_graph('{GRAPH_NAME}');")
    conn.commit()
    print(f"  ✓ Graph '{GRAPH_NAME}' created")


def create_contract_nodes(cur, conn):
    """Create Contract nodes."""
    print("\n📄 Creating Contract nodes...")
    
    # Fetch contracts
    cur.execute("""
        SELECT c.id, c.contract_identifier, c.title, c.contract_type, 
               c.effective_date, c.expiration_date, c.governing_law,
               j.name as jurisdiction_name
        FROM contracts c
        LEFT JOIN jurisdictions j ON c.jurisdiction_id = j.id
    """)
    contracts = cur.fetchall()
    
    count = 0
    for contract in contracts:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            CREATE (c:Contract {{
                db_id: {contract['id']},
                identifier: '{contract['contract_identifier']}',
                title: '{contract['title'].replace("'", "\'")}',
                type: '{contract['contract_type'] or 'Unknown'}',
                effective_date: '{contract['effective_date'] or ''}',
                expiration_date: '{contract['expiration_date'] or ''}',
                governing_law: '{contract['governing_law'] or ''}',
                jurisdiction: '{contract['jurisdiction_name'] or ''}'
            }})
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
        count += 1
    
    conn.commit()
    print(f"  ✓ Created {count} Contract nodes")


def create_party_nodes(cur, conn):
    """Create Party nodes."""
    print("\n👤 Creating Party nodes...")
    
    cur.execute("""
        SELECT p.id, p.name, p.party_type, p.address,
               j.name as jurisdiction_name
        FROM parties p
        LEFT JOIN jurisdictions j ON p.jurisdiction_id = j.id
    """)
    parties = cur.fetchall()
    
    count = 0
    for party in parties:
        party_name = party['name'].replace("'", "\\'")
        
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            CREATE (p:Party {{
                db_id: {party['id']},
                name: '{party_name}',
                type: '{party['party_type'] or 'Unknown'}',
                address: '{(party['address'] or '').replace("'", "\\'")[:100]}',
                jurisdiction: '{party['jurisdiction_name'] or ''}'
            }})
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
        count += 1
    
    conn.commit()
    print(f"  ✓ Created {count} Party nodes")


def create_clause_nodes(cur, conn):
    """Create Clause nodes."""
    print("\n📝 Creating Clause nodes...")
    
    cur.execute("""
        SELECT cl.id, cl.contract_id, cl.section_label, cl.title, 
               cl.risk_level, cl.is_standard, cl.position_in_contract,
               ct.name as clause_type_name
        FROM clauses cl
        LEFT JOIN clause_types ct ON cl.clause_type_id = ct.id
        ORDER BY cl.contract_id, cl.position_in_contract
    """)
    clauses = cur.fetchall()
    
    count = 0
    batch_size = 20
    
    for i in range(0, len(clauses), batch_size):
        batch = clauses[i:i+batch_size]
        
        for clause in batch:
            section = (clause['section_label'] or '').replace("'", "\\'")[:100]
            title = (clause['title'] or '').replace("'", "\\'")[:100]
            
            cypher = f"""
            SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
                CREATE (cl:Clause {{
                    db_id: {clause['id']},
                    contract_db_id: {clause['contract_id']},
                    section: '{section}',
                    title: '{title}',
                    type: '{clause['clause_type_name'] or 'Other'}',
                    risk_level: '{clause['risk_level']}',
                    is_standard: {str(clause['is_standard']).lower()},
                    position: {clause['position_in_contract']}
                }})
            $$) as (result agtype);
            """
            
            execute_age_query(cur, cypher)
            count += 1
        
        conn.commit()
        if count % 50 == 0:
            print(f"    Created {count}/{len(clauses)} clauses...")
    
    print(f"  ✓ Created {count} Clause nodes")


def create_obligation_nodes(cur, conn):
    """Create Obligation nodes."""
    print("\n⚖️ Creating Obligation nodes...")
    
    cur.execute("""
        SELECT o.id, o.clause_id, o.description, o.responsible_party_id,
               o.beneficiary_party_id, o.penalty_description, o.is_high_impact
        FROM obligations o
    """)
    obligations = cur.fetchall()
    
    count = 0
    for obligation in obligations:
        description = obligation['description'].replace("'", "\\'")[:200]
        penalty = (obligation['penalty_description'] or '').replace("'", "\\'")[:100]
        
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            CREATE (o:Obligation {{
                db_id: {obligation['id']},
                clause_db_id: {obligation['clause_id']},
                description: '{description}',
                responsible_party_db_id: {obligation['responsible_party_id'] or 'null'},
                beneficiary_party_db_id: {obligation['beneficiary_party_id'] or 'null'},
                penalty: '{penalty}',
                is_high_impact: {str(obligation['is_high_impact']).lower()}
            }})
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
        count += 1
    
    conn.commit()
    print(f"  ✓ Created {count} Obligation nodes")


def create_right_nodes(cur, conn):
    """Create Right nodes."""
    print("\n✅ Creating Right nodes...")
    
    cur.execute("""
        SELECT r.id, r.clause_id, r.description, r.holder_party_id, r.condition_description
        FROM rights r
    """)
    rights = cur.fetchall()
    
    count = 0
    for right in rights:
        description = right['description'].replace("'", "\\'")[:200]
        condition = (right['condition_description'] or '').replace("'", "\\'")[:100]
        
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            CREATE (r:Right {{
                db_id: {right['id']},
                clause_db_id: {right['clause_id']},
                description: '{description}',
                holder_party_db_id: {right['holder_party_id'] or 'null'},
                condition: '{condition}'
            }})
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
        count += 1
    
    conn.commit()
    print(f"  ✓ Created {count} Right nodes")


def create_term_nodes(cur, conn):
    """Create Term Definition nodes."""
    print("\n📖 Creating Term nodes...")
    
    cur.execute("""
        SELECT td.id, td.contract_id, td.term_name, td.definition_text
        FROM term_definitions td
    """)
    terms = cur.fetchall()
    
    count = 0
    for term in terms:
        term_name = term['term_name'].replace("'", "\\'")[:50]
        definition = (term['definition_text'] or '').replace("'", "\\'")[:200]
        
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            CREATE (t:Term {{
                db_id: {term['id']},
                contract_db_id: {term['contract_id']},
                name: '{term_name}',
                definition: '{definition}'
            }})
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
        count += 1
    
    conn.commit()
    print(f"  ✓ Created {count} Term nodes")


def create_relationships(cur, conn):
    """Create all relationships."""
    print("\n🔗 Creating Relationships...")
    
    # IS_PARTY_TO relationships
    print("  Creating IS_PARTY_TO edges...")
    cur.execute("""
        SELECT pc.party_id, pc.contract_id, pr.name as role_name
        FROM parties_contracts pc
        LEFT JOIN party_roles pr ON pc.role_id = pr.id
    """)
    party_contracts = cur.fetchall()
    
    for pc in party_contracts:
        role = (pc['role_name'] or 'Unknown').replace("'", "\\'")
        
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (p:Party {{db_id: {pc['party_id']}}}), 
                  (c:Contract {{db_id: {pc['contract_id']}}})
            CREATE (p)-[:IS_PARTY_TO {{role: '{role}'}}]->(c)
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
    
    conn.commit()
    print(f"    ✓ Created {len(party_contracts)} IS_PARTY_TO edges")
    
    # CONTAINS_CLAUSE relationships
    print("  Creating CONTAINS_CLAUSE edges...")
    cur.execute("SELECT id, contract_id FROM clauses")
    clauses = cur.fetchall()
    
    for clause in clauses:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (c:Contract {{db_id: {clause['contract_id']}}}), 
                  (cl:Clause {{db_id: {clause['id']}}})
            CREATE (c)-[:CONTAINS_CLAUSE]->(cl)
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
    
    conn.commit()
    print(f"    ✓ Created {len(clauses)} CONTAINS_CLAUSE edges")
    
    # IMPOSES_OBLIGATION relationships
    print("  Creating IMPOSES_OBLIGATION edges...")
    cur.execute("SELECT id, clause_id FROM obligations")
    obligations = cur.fetchall()
    
    for obligation in obligations:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (cl:Clause {{db_id: {obligation['clause_id']}}}), 
                  (o:Obligation {{db_id: {obligation['id']}}})
            CREATE (cl)-[:IMPOSES_OBLIGATION]->(o)
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
    
    conn.commit()
    print(f"    ✓ Created {len(obligations)} IMPOSES_OBLIGATION edges")
    
    # RESPONSIBLE_FOR relationships (Party -> Obligation)
    print("  Creating RESPONSIBLE_FOR edges...")
    cur.execute("""
        SELECT id, responsible_party_id 
        FROM obligations 
        WHERE responsible_party_id IS NOT NULL
    """)
    responsible = cur.fetchall()
    
    for obligation in responsible:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (p:Party {{db_id: {obligation['responsible_party_id']}}}), 
                  (o:Obligation {{db_id: {obligation['id']}}})
            CREATE (p)-[:RESPONSIBLE_FOR]->(o)
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
    
    conn.commit()
    print(f"    ✓ Created {len(responsible)} RESPONSIBLE_FOR edges")
    
    # GRANTS_RIGHT relationships
    print("  Creating GRANTS_RIGHT edges...")
    cur.execute("SELECT id, clause_id FROM rights")
    rights = cur.fetchall()
    
    for right in rights:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (cl:Clause {{db_id: {right['clause_id']}}}), 
                  (r:Right {{db_id: {right['id']}}})
            CREATE (cl)-[:GRANTS_RIGHT]->(r)
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
    
    conn.commit()
    print(f"    ✓ Created {len(rights)} GRANTS_RIGHT edges")
    
    # HOLDS_RIGHT relationships (Party -> Right)
    print("  Creating HOLDS_RIGHT edges...")
    cur.execute("""
        SELECT id, holder_party_id 
        FROM rights 
        WHERE holder_party_id IS NOT NULL
    """)
    holders = cur.fetchall()
    
    for right in holders:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (p:Party {{db_id: {right['holder_party_id']}}}), 
                  (r:Right {{db_id: {right['id']}}})
            CREATE (p)-[:HOLDS_RIGHT]->(r)
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
    
    conn.commit()
    print(f"    ✓ Created {len(holders)} HOLDS_RIGHT edges")
    
    # DEFINES_TERM relationships
    print("  Creating DEFINES_TERM edges...")
    cur.execute("SELECT id, contract_id FROM term_definitions")
    terms = cur.fetchall()
    
    for term in terms:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (c:Contract {{db_id: {term['contract_id']}}}), 
                  (t:Term {{db_id: {term['id']}}})
            CREATE (c)-[:DEFINES_TERM]->(t)
        $$) as (result agtype);
        """
        
        execute_age_query(cur, cypher)
    
    conn.commit()
    print(f"    ✓ Created {len(terms)} DEFINES_TERM edges")


def print_graph_statistics(cur):
    """Display graph statistics."""
    print("\n" + "=" * 70)
    print("📊 Graph Statistics")
    print("=" * 70)
    
    # Count nodes by type
    node_types = ['Contract', 'Party', 'Clause', 'Obligation', 'Right', 'Term']
    
    for node_type in node_types:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH (n:{node_type})
            RETURN count(n) as count
        $$) as (count agtype);
        """
        
        result = execute_age_query(cur, cypher)
        if result:
            count = result[0]['count']
            print(f"  {node_type} nodes: {count}")
    
    # Count relationships
    print("\n  Relationships:")
    rel_types = ['IS_PARTY_TO', 'CONTAINS_CLAUSE', 'IMPOSES_OBLIGATION', 
                 'RESPONSIBLE_FOR', 'GRANTS_RIGHT', 'HOLDS_RIGHT', 'DEFINES_TERM']
    
    for rel_type in rel_types:
        cypher = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            MATCH ()-[r:{rel_type}]->()
            RETURN count(r) as count
        $$) as (count agtype);
        """
        
        result = execute_age_query(cur, cypher)
        if result:
            count = result[0]['count']
            print(f"    {rel_type}: {count}")
    
    print("=" * 70)


def test_graph_query(cur):
    """Test multi-hop graph traversal."""
    print("\n🔍 Testing Multi-Hop Graph Query")
    print("Query: Find all obligations for parties in contracts")
    print("-" * 70)
    
    cypher = f"""
    SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
        MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)-[:IMPOSES_OBLIGATION]->(o:Obligation)
        WHERE p.name <> ''
        RETURN p.name as party, c.title as contract, 
               cl.section as clause_section, o.description as obligation
        LIMIT 5
    $$) as (party agtype, contract agtype, clause_section agtype, obligation agtype);
    """
    
    results = execute_age_query(cur, cypher)
    
    for row in results:
        print(f"\n  Party: {row['party']}")
        print(f"  Contract: {row['contract']}")
        print(f"  Clause: {row['clause_section']}")
        print(f"  Obligation: {row['obligation']}")
    
    print("-" * 70)


def main():
    """Main graph creation pipeline."""
    print("=" * 70)
    print("Contract Intelligence - Apache AGE Graph Builder")
    print("=" * 70)
    
    if not DB_PASSWORD:
        print("❌ ERROR: POSTGRES_ADMIN_PASSWORD not set")
        return
    
    # Connect to database
    print("\n🔌 Connecting to PostgreSQL...")
    conn = get_db_connection()
    cur = conn.cursor()
    print("✓ Connected")
    
    # Set search path for AGE (extension is pre-loaded via shared_preload_libraries)
    print("\n🔧 Setting up Apache AGE...")
    cur.execute("SET search_path = ag_catalog, '$user', public;")
    conn.commit()
    print("✓ AGE ready")
    
    # Create graph
    create_graph(cur, conn)
    
    # Create nodes
    create_contract_nodes(cur, conn)
    create_party_nodes(cur, conn)
    create_clause_nodes(cur, conn)
    create_obligation_nodes(cur, conn)
    create_right_nodes(cur, conn)
    create_term_nodes(cur, conn)
    
    # Create relationships
    create_relationships(cur, conn)
    
    # Print statistics
    print_graph_statistics(cur)
    
    # Test query
    test_graph_query(cur)
    
    print("\n✅ Graph creation complete!")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
