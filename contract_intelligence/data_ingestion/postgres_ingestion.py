#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
PostgreSQL Ingestion Module

Handles contract extraction and storage in PostgreSQL database.
"""

import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

from contract_extractor import (
    extract_contract_metadata,
    segment_clauses,
    classify_and_analyze_clause,
    get_embedding
)

# Load environment
load_dotenv()

# Database configuration
DB_HOST = os.environ.get("POSTGRES_HOST", "ci-ci-dev-pgflex.postgres.database.azure.com")
DB_NAME = os.environ.get("POSTGRES_DATABASE", "cipgraph")
DB_USER = os.environ.get("POSTGRES_USER", "pgadmin")
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")

# Paths - resolve relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / "data" / "input"
SCHEMA_FILE = Path(__file__).parent / "schema.sql"  # schema.sql now in data_ingestion/


def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require',
        cursor_factory=RealDictCursor
    )


def initialize_schema(schema_file_path: Path = None) -> bool:
    """Initialize PostgreSQL schema from SQL file."""
    if schema_file_path is None:
        schema_file_path = SCHEMA_FILE
    
    print("\n[*] Initializing PostgreSQL schema...")
    print(f"    This will DROP all existing tables and recreate them!")
    
    if not schema_file_path.exists():
        print(f"[!] Schema file not found: {schema_file_path}")
        return False
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Read and display schema info
        with open(schema_file_path, 'r') as f:
            schema_sql = f.read()
        
        # Check for VARCHAR limits in schema
        import re
        varchar_limits = re.findall(r'VARCHAR\((\d+)\)', schema_sql)
        print(f"    VARCHAR limits in schema: {set(varchar_limits)}")
        
        cur.execute(schema_sql)
        conn.commit()
        cur.close()
        conn.close()
        print("[OK] Schema initialized with updated VARCHAR limits")
        return True
    except Exception as e:
        print(f"[!] Schema initialization error: {e}")
        return False


def test_connection() -> bool:
    """Test PostgreSQL database connection."""
    print("\n[*] Testing PostgreSQL connection...")
    try:
        test_conn = get_db_connection()
        test_cur = test_conn.cursor()
        test_cur.execute("SELECT version();")
        version = test_cur.fetchone()
        print(f"[OK] Connected to PostgreSQL")
        print(f"    Version: {version['version'][:80]}...")
        test_cur.close()
        test_conn.close()
        return True
    except Exception as e:
        print(f"[X] Connection failed: {e}")
        return False


def ingest_contract_comprehensive(filepath: Path):
    """Comprehensive contract ingestion with rich ontology."""
    print(f"\n📄 Processing: {filepath.name}")
    
    # Create dedicated connection for this contract
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Read content
        with open(filepath, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    
        # Extract metadata
        print("  🔍 Extracting metadata...")
        metadata = extract_contract_metadata(markdown_content, filepath.name)
        
        # Truncate long values with logging
        def truncate_field(value: str, max_length: int, field_name: str) -> str:
            if value and len(value) > max_length:
                print(f"  ⚠️  Truncating {field_name}: '{value}' ({len(value)} chars) -> {max_length} chars")
                return value[:max_length]
            return value
        
        # Debug: Log all metadata fields
        print(f"  DEBUG: governing_law = {metadata.get('governing_law')} ({len(metadata.get('governing_law', '')) if metadata.get('governing_law') else 0} chars)")
        print(f"  DEBUG: contract_type = {metadata.get('contract_type')} ({len(metadata.get('contract_type', '')) if metadata.get('contract_type') else 0} chars)")
        print(f"  DEBUG: parties count = {len(metadata.get('parties', []))}")
        for i, party in enumerate(metadata.get('parties', [])):
            print(f"  DEBUG: party[{i}].name = {party.get('name')} ({len(party.get('name', '')) if party.get('name') else 0} chars)")
            print(f"  DEBUG: party[{i}].role = {party.get('role')} ({len(party.get('role', '')) if party.get('role') else 0} chars)")
            print(f"  DEBUG: party[{i}].jurisdiction = {party.get('jurisdiction')} ({len(party.get('jurisdiction', '')) if party.get('jurisdiction') else 0} chars)")
        
        # Truncate governing_law if too long
        governing_law = truncate_field(metadata.get("governing_law"), 200, "governing_law")
        
        # Create contract identifier
        contract_id_parts = filepath.stem.split('_')
        contract_identifier = f"{contract_id_parts[0]}_{contract_id_parts[1]}" if len(contract_id_parts) >= 2 else filepath.stem
        
        # Insert contract
        cur.execute("""
            INSERT INTO contracts (contract_identifier, reference_number, title, contract_type, effective_date, 
                                expiration_date, governing_law, source_file_path, source_markdown)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (contract_identifier) DO UPDATE 
            SET title = EXCLUDED.title, reference_number = EXCLUDED.reference_number, updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            contract_identifier,
            metadata.get("reference_number"),
            metadata.get("title", filepath.stem),
            metadata.get("contract_type"),
            metadata.get("effective_date"),
            metadata.get("expiration_date"),
            governing_law,
            str(filepath),
            markdown_content
        ))
        
        contract_id = cur.fetchone()['id']
        conn.commit()
        print(f"  ✓ Contract created (ID: {contract_id}, Ref: {metadata.get('reference_number', 'N/A')})")
        
        # Insert jurisdiction if governing_law specified
        jurisdiction_id = None
        if governing_law:
            jurisdiction_name = truncate_field(governing_law, 300, "jurisdiction.name")
            cur.execute("""
                INSERT INTO jurisdictions (name, country, state_province)
                VALUES (%s, %s, %s)
                ON CONFLICT (name, country, state_province) DO UPDATE 
                SET name = EXCLUDED.name
                RETURNING id
            """, (jurisdiction_name, None, None))
            jurisdiction_id = cur.fetchone()['id']
            
            cur.execute("""
                UPDATE contracts SET jurisdiction_id = %s WHERE id = %s
            """, (jurisdiction_id, contract_id))
            conn.commit()
        
        # Insert parties with jurisdictions
        party_map = {}  # name -> party_id
        parties_data = metadata.get("parties", [])
        
        for party_info in parties_data:
            party_name = party_info.get("name")
            if not party_name:
                continue
            
            # Truncate party name if needed
            party_name = truncate_field(party_name, 300, f"party.name")
            
            party_jurisdiction_id = None
            if party_info.get("jurisdiction"):
                party_jurisdiction = truncate_field(party_info["jurisdiction"], 300, "party.jurisdiction")
                cur.execute("""
                    INSERT INTO jurisdictions (name, country, state_province)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name, country, state_province) DO UPDATE 
                    SET name = EXCLUDED.name
                    RETURNING id
                """, (party_jurisdiction, None, None))
                party_jurisdiction_id = cur.fetchone()['id']
            
            # Truncate address if needed
            party_address = truncate_field(party_info.get("address"), 1000, "party.address")
            
            cur.execute("""
                INSERT INTO parties (name, party_type, address, jurisdiction_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (tenant_id, name) DO UPDATE 
                SET address = EXCLUDED.address, updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (party_name, "Corporation", party_address, party_jurisdiction_id))
            
            party_id = cur.fetchone()['id']
            party_map[party_name] = party_id
            
            # Link party to contract
            party_role = party_info.get("role", "Unknown")
            # Truncate role name to fit lookup table (50 chars)
            party_role = truncate_field(party_role, 50, "party.role")
            cur.execute("SELECT id FROM party_roles WHERE name = %s", (party_role,))
            role_row = cur.fetchone()
            role_id = role_row['id'] if role_row else None
            
            cur.execute("""
                INSERT INTO parties_contracts (party_id, contract_id, role_id, role_description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (party_id, contract_id, role_id) DO NOTHING
            """, (party_id, contract_id, role_id, party_role))
        
        conn.commit()
        print(f"  ✓ Parties linked: {len(parties_data)}")
        
        # Insert defined terms
        for term_info in metadata.get("defined_terms", []):
            cur.execute("""
                INSERT INTO term_definitions (contract_id, term_name, definition_text)
                VALUES (%s, %s, %s)
                ON CONFLICT (contract_id, term_name) DO NOTHING
            """, (contract_id, term_info["term"], term_info["definition"]))
        
        conn.commit()
        
        # Insert contract relationship if this is a related contract
        parent_ref = metadata.get("parent_contract_reference")
        relationship_type = metadata.get("relationship_type")
        relationship_desc = metadata.get("relationship_description")
        
        if parent_ref:
            print(f"  🔗 Detected relationship to parent: {parent_ref}")
            
            # Find parent contract in database by reference number
            parent_contract_id = None
            cur.execute("SELECT id FROM contracts WHERE reference_number = %s", (parent_ref,))
            parent_row = cur.fetchone()
            if parent_row:
                parent_contract_id = parent_row['id']
            
            # Determine relationship type from contract type if not explicitly set
            if not relationship_type:
                contract_type_lower = metadata.get("contract_type", "").lower()
                if "amendment" in contract_type_lower:
                    relationship_type = "amendment"
                elif "statement of work" in contract_type_lower or "sow" in contract_type_lower:
                    relationship_type = "sow"
                elif "addendum" in contract_type_lower:
                    relationship_type = "addendum"
                elif "work order" in contract_type_lower:
                    relationship_type = "work_order"
                elif "maintenance" in contract_type_lower:
                    relationship_type = "maintenance"
                else:
                    relationship_type = "related"
            
            # Insert relationship record (even if parent not found yet)
            cur.execute("""
                INSERT INTO contract_relationships (child_contract_id, parent_contract_id, 
                                                  parent_reference_number,
                                                  relationship_type, relationship_description)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (child_contract_id, parent_contract_id, relationship_type) DO NOTHING
            """, (
                contract_id,
                parent_contract_id,  # May be NULL if parent not ingested yet
                parent_ref,
                relationship_type,
                relationship_desc
            ))
            conn.commit()
            
            if parent_contract_id:
                print(f"  ✓ Linked to parent contract (ID: {parent_contract_id}) as {relationship_type}")
            else:
                print(f"  ⚠ Parent contract not yet ingested - relationship recorded for later resolution")
        
        # Insert total contract value
        total_value = metadata.get("total_value")
        if total_value and total_value.get("amount"):
            cur.execute("""
                INSERT INTO monetary_values (contract_id, amount, currency, value_type, context)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                contract_id,
                total_value["amount"],
                total_value.get("currency", "USD"),
                "Total Contract Value",
                total_value.get("description")
            ))
            conn.commit()
        
        # Segment and analyze clauses
        print("  📝 Segmenting clauses...")
        clauses_data = segment_clauses(markdown_content)
        print(f"  ✓ Found {len(clauses_data)} clauses")
        
        print("  🧠 Analyzing clauses with LLM...")
        clause_count = 0
        
        for i, clause_data in enumerate(clauses_data):
            if i % 3 == 0:
                print(f"    Processing clause {i+1}/{len(clauses_data)}...")
            
            # Analyze clause comprehensively
            analysis = classify_and_analyze_clause(
                clause_data["text_content"],
                clause_data.get("title", "")
            )
            
            # Get clause_type_id
            cur.execute("SELECT id FROM clause_types WHERE name = %s", (analysis["clause_type"],))
            clause_type_row = cur.fetchone()
            clause_type_id = clause_type_row['id'] if clause_type_row else None
            
            # Generate embedding
            embedding = get_embedding(clause_data["text_content"])
            
            # Insert clause
            cur.execute("""
                INSERT INTO clauses (contract_id, section_label, title, clause_type_id, 
                                risk_level, is_standard, text_content, embedding, position_in_contract)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                contract_id,
                clause_data["section_label"],
                clause_data["title"],
                clause_type_id,
                analysis["risk_level"],
                analysis["is_standard"],
                clause_data["text_content"],
                embedding,
                clause_data["position"]
            ))
            
            clause_id = cur.fetchone()['id']
            
            # Insert obligations
            for obligation in analysis.get("obligations", []):
                responsible_party_id = party_map.get(obligation.get("responsible_party"))
                beneficiary_party_id = party_map.get(obligation.get("beneficiary_party"))
                
                cur.execute("""
                    INSERT INTO obligations (clause_id, description, responsible_party_id, 
                                        beneficiary_party_id, penalty_description, is_high_impact)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    clause_id,
                    obligation["description"],
                    responsible_party_id,
                    beneficiary_party_id,
                    obligation.get("penalty_description"),
                    obligation.get("is_high_impact", False)
                ))
            
            # Insert rights
            for right in analysis.get("rights", []):
                holder_party_id = party_map.get(right.get("holder_party"))
                
                cur.execute("""
                    INSERT INTO rights (clause_id, description, holder_party_id, condition_description)
                    VALUES (%s, %s, %s, %s)
                """, (
                    clause_id,
                    right["description"],
                    holder_party_id,
                    right.get("condition_description")
                ))
            
            # Insert monetary values
            for monetary in analysis.get("monetary_values", []):
                if monetary.get("amount"):
                    # Truncate fields that might exceed old schema limits
                    value_type = truncate_field(monetary.get("value_type"), 200, "monetary.value_type")
                    context = truncate_field(monetary.get("context"), 1000, "monetary.context")
                    
                    cur.execute("""
                        INSERT INTO monetary_values (contract_id, clause_id, amount, currency, 
                                                value_type, context, multiple_of_fees)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        contract_id,
                        clause_id,
                        monetary["amount"],
                        monetary.get("currency", "USD"),
                        value_type,
                        context,
                        monetary.get("multiple_of_fees")
                    ))
            
            # Insert conditions
            for condition in analysis.get("conditions", []):
                cur.execute("""
                    INSERT INTO conditions (description, trigger_event)
                    VALUES (%s, %s)
                """, (
                    condition["description"],
                    condition.get("trigger_event")
                ))
            
            # If high risk, create risk entry
            if analysis["risk_level"] in ["high", "medium"] and analysis.get("risk_rationale"):
                cur.execute("""
                    INSERT INTO risks (contract_id, clause_id, risk_type_custom, risk_level, 
                                    rationale, detected_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    contract_id,
                    clause_id,
                    analysis["clause_type"],
                    analysis["risk_level"],
                    analysis["risk_rationale"],
                    "LLM Analysis"
                ))
            
            clause_count += 1
            
            # Commit every 5 clauses
            if clause_count % 5 == 0:
                conn.commit()
        
        conn.commit()
        print(f"  ✓ Clauses analyzed: {clause_count}")
        
        # Show extraction summary
        cur.execute("SELECT COUNT(*) as cnt FROM obligations WHERE clause_id IN (SELECT id FROM clauses WHERE contract_id = %s)", (contract_id,))
        obligation_count = cur.fetchone()['cnt']
        
        cur.execute("SELECT COUNT(*) as cnt FROM rights WHERE clause_id IN (SELECT id FROM clauses WHERE contract_id = %s)", (contract_id,))
        right_count = cur.fetchone()['cnt']
        
        cur.execute("SELECT COUNT(*) as cnt FROM monetary_values WHERE contract_id = %s", (contract_id,))
        monetary_count = cur.fetchone()['cnt']
        
        print(f"  📊 Extracted: {obligation_count} obligations, {right_count} rights, {monetary_count} monetary values")
        
        return contract_id
    
    finally:
        # Always close connection
        cur.close()
        conn.close()


def process_single_contract(filepath: Path) -> tuple[str, bool, str]:
    """Process a single contract and return result."""
    try:
        ingest_contract_comprehensive(filepath)
        return (filepath.name, True, "Success")
    except Exception as e:
        # Provide more detailed error information
        import traceback
        error_msg = str(e)
        full_trace = traceback.format_exc()
        
        # Try to extract the specific column causing the issue
        if "value too long" in error_msg.lower():
            # Parse psycopg2 error to find column name
            print(f"\n  ❌ ERROR DETAILS for {filepath.name}:")
            print(f"     Error: {error_msg}")
            print(f"     Full trace:\n{full_trace}")
            error_msg = f"VARCHAR limit exceeded: {error_msg}"
        
        return (filepath.name, False, error_msg)


def resolve_orphaned_relationships() -> int:
    """Resolve contract relationships where parent_contract_id was NULL.
    
    This happens when a child contract is ingested before its parent.
    After all contracts are ingested, we can resolve these orphaned relationships.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Find relationships with NULL parent_contract_id but non-NULL parent reference
        cur.execute("""
            SELECT id, parent_reference_number
            FROM contract_relationships
            WHERE parent_contract_id IS NULL
            AND parent_reference_number IS NOT NULL
        """)
        
        orphaned = cur.fetchall()
        resolved_count = 0
        
        for row in orphaned:
            relationship_id = row['id']
            parent_ref = row['parent_reference_number']
            
            # Try to find parent by reference number
            if parent_ref:
                cur.execute("SELECT id FROM contracts WHERE reference_number = %s", (parent_ref,))
                parent_row = cur.fetchone()
                if parent_row:
                    parent_contract_id = parent_row['id']
                    
                    # Update the relationship
                    cur.execute("""
                        UPDATE contract_relationships
                        SET parent_contract_id = %s
                        WHERE id = %s
                    """, (parent_contract_id, relationship_id))
                    resolved_count += 1
        
        conn.commit()
        return resolved_count
    
    finally:
        cur.close()
        conn.close()


def get_database_statistics() -> dict:
    """Get comprehensive database statistics."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        stats = {}
        tables = [
            'contracts', 'clauses', 'obligations', 'rights', 
            'monetary_values', 'risks', 'term_definitions', 
            'parties', 'jurisdictions', 'contract_relationships'
        ]
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) as cnt FROM {table}")
                stats[table] = cur.fetchone()['cnt']
            except Exception:
                stats[table] = 'N/A'
        
        cur.close()
        conn.close()
        
        return stats
    except Exception as e:
        print(f"[!] Statistics query failed: {e}")
        return {}


def get_sample_contract_info():
    """Get information about the most recently processed contract."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                contract_identifier,
                title,
                contract_type,
                effective_date,
                governing_law,
                (SELECT COUNT(*) FROM clauses WHERE contract_id = contracts.id) as clause_count,
                (SELECT COUNT(*) FROM obligations o 
                 JOIN clauses c ON o.clause_id = c.id 
                 WHERE c.contract_id = contracts.id) as obligation_count
            FROM contracts
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return result
    except Exception:
        return None


def process_contracts(
    contract_files: list[Path], 
    num_to_process: int = None,
    n_parallel: int = 5
) -> tuple[int, int, list]:
    """
    Process contract files into PostgreSQL.
    
    Args:
        contract_files: List of contract file paths
        num_to_process: Number of contracts to process (None = all)
        n_parallel: Number of parallel workers
        
    Returns:
        (successful_count, failed_count, failed_files_list)
    """
    if num_to_process is None:
        num_to_process = len(contract_files)
    
    files_to_process = contract_files[:num_to_process]
    
    print(f"\n[*] Processing {num_to_process} contracts with {n_parallel} parallel workers...")
    print(f"    Extracting: metadata, clauses, obligations, rights, monetary values")
    
    successful = 0
    failed = 0
    failed_files = []
    
    with ThreadPoolExecutor(max_workers=n_parallel) as executor:
        future_to_file = {
            executor.submit(process_single_contract, filepath): filepath 
            for filepath in files_to_process
        }
        
        for future in as_completed(future_to_file):
            filename, success, message = future.result()
            
            if success:
                successful += 1
                print(f"  [OK] {filename}")
            else:
                failed += 1
                failed_files.append((filename, message))
                print(f"  [X] {filename} - {message}")
    
    return successful, failed, failed_files


def run_postgres_ingestion(
    num_contracts: int = None,
    n_parallel: int = 8,
    skip_schema_init: bool = False
) -> bool:
    """
    Main entry point for PostgreSQL ingestion.
    
    Args:
        num_contracts: Number of contracts to process (None = all)
        n_parallel: Number of parallel workers
        skip_schema_init: Skip schema initialization if True
        
    Returns:
        True if successful, False otherwise
    """
    print("=" * 70)
    print("PostgreSQL Contract Ingestion")
    print("=" * 70)
    
    # Validate configuration
    if not DB_PASSWORD:
        print("[X] ERROR: POSTGRES_ADMIN_PASSWORD not set")
        return False
    
    # Test connection
    if not test_connection():
        return False
    
    # Initialize schema
    if not skip_schema_init:
        initialize_schema()
    
    # Find contract files
    contract_files = sorted(INPUT_DIR.glob("contract_*.md"))
    print(f"\n[*] Found {len(contract_files)} contract files")
    
    if not contract_files:
        print("[!] No contract files found in data/input/")
        return False
    
    # Process contracts
    successful, failed, failed_files = process_contracts(
        contract_files,
        num_to_process=num_contracts,
        n_parallel=n_parallel
    )
    
    # Show failures
    if failed_files:
        print(f"\n[!] Failed contracts:")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")
    
    # Summary
    total = num_contracts if num_contracts else len(contract_files)
    print("\n" + "=" * 70)
    print(f"PostgreSQL Ingestion Complete: {successful}/{total} successful")
    print("=" * 70)
    
    # Run data exploration if ingestion was successful
    if successful > 0:
        print("\n" + "=" * 70)
        print("Running Data Exploration & Report Generation")
        print("=" * 70)
        try:
            import subprocess
            explore_script = Path(__file__).parent / 'explore_data.py'
            result = subprocess.run(
                [sys.executable, str(explore_script)],
                capture_output=False,
                text=True
            )
            if result.returncode == 0:
                print("\n✅ Data exploration report generated successfully!")
            else:
                print("\n⚠️ Data exploration completed with warnings")
        except Exception as e:
            print(f"\n⚠️ Could not run data exploration: {e}")
            print("You can run it manually: python data_ingestion/explore_data.py")
    
    # Resolve orphaned relationships (child contracts ingested before parents)
    if successful > 0:
        print("\n[*] Resolving orphaned contract relationships...")
        resolved = resolve_orphaned_relationships()
        if resolved > 0:
            print(f"  ✓ Resolved {resolved} orphaned relationships")
    
    # Get statistics
    print("\n[*] Database Statistics:")
    stats = get_database_statistics()
    
    if stats:
        print(f"    Contracts: {stats.get('contracts', 'N/A')}")
        print(f"    Parties: {stats.get('parties', 'N/A')}")
        print(f"    Clauses: {stats.get('clauses', 'N/A')}")
        print(f"    Obligations: {stats.get('obligations', 'N/A')}")
        print(f"    Rights: {stats.get('rights', 'N/A')}")
        print(f"    Monetary Values: {stats.get('monetary_values', 'N/A')}")
        print(f"    Risks: {stats.get('risks', 'N/A')}")
        print(f"    Relationships: {stats.get('contract_relationships', 'N/A')}")
        
        # Show sample contract
        sample = get_sample_contract_info()
        if sample:
            print(f"\n[*] Latest Contract:")
            print(f"    {sample['contract_identifier']}: {sample['title'][:50]}...")
            print(f"    Type: {sample['contract_type']}, Clauses: {sample['clause_count']}, Obligations: {sample['obligation_count']}")
    
    return successful > 0


if __name__ == "__main__":
    """Standalone execution - interactive mode."""
    print("\n[?] How many contracts to process?")
    print("    1 = Quick test (1 contract)")
    print("    5 = Moderate test (5 contracts)")
    print("    20 = Medium batch (20 contracts)")
    print("    a = Full ingestion (all contracts)")
    
    choice = input("\nChoice [1/5/20/a]: ").strip().lower()
    
    if choice == '1':
        num, workers = 1, 1
    elif choice == '5':
        num, workers = 5, 2
    elif choice == '20':
        num, workers = 20, 10
    else:
        num, workers = None, 20
    
    success = run_postgres_ingestion(num_contracts=num, n_parallel=workers)
    print("\n" + ("✓ Success!" if success else "✗ Failed"))
