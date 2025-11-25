#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Comprehensive Contract Extraction Pipeline

Rich ontology extraction using LLM to extract:
- Entities: Contracts, Parties, Clauses, Obligations, Rights, Terms, Conditions, MonetaryValues
- Relationships: IS_PARTY_TO, CONTAINS_CLAUSE, IMPOSES_OBLIGATION, GRANTS_RIGHT, etc.
- Graph edges using Apache AGE for multi-hop reasoning
"""

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
DB_HOST = os.environ.get("POSTGRES_HOST", "ci-ci-dev-pgflex.postgres.database.azure.com")
DB_NAME = os.environ.get("POSTGRES_DATABASE", "cipgraph")
DB_USER = os.environ.get("POSTGRES_USER", "pgadmin")
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")
INPUT_DIR = Path("data/input")

# Validate required environment variables
GRAPHRAG_API_KEY = os.environ.get("GRAPHRAG_API_KEY")
GRAPHRAG_API_BASE = os.environ.get("GRAPHRAG_API_BASE")

if not GRAPHRAG_API_KEY:
    raise ValueError("GRAPHRAG_API_KEY environment variable is required")
if not GRAPHRAG_API_BASE:
    raise ValueError("GRAPHRAG_API_BASE environment variable is required")

# OpenAI client
openai_client = OpenAI(
    api_key=GRAPHRAG_API_KEY,
    base_url=GRAPHRAG_API_BASE + "/openai/v1/" if not GRAPHRAG_API_BASE.endswith("/") else GRAPHRAG_API_BASE + "openai/v1/"
)

LLM_MODEL = os.environ.get("GRAPHRAG_LLM_DEPLOYMENT_NAME", "gpt-4.1")
EMBEDDING_MODEL = os.environ.get("GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small")


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


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for text using Azure OpenAI."""
    response = openai_client.embeddings.create(
        input=text[:8000],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0) -> str:
    """Call LLM with system and user prompts."""
    try:
        response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # temperature=temperature
        )
        
        result = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        
        return result.strip()
    
    except Exception as e:
        print(f"    ⚠ LLM call error: {e}")
        return None


def extract_contract_metadata(markdown_content: str, filename: str) -> dict[str, Any]:
    """Extract comprehensive contract metadata using LLM."""
    
    system_prompt = """You are a legal contract analyzer specialized in extracting structured metadata.
Extract information accurately and return ONLY valid JSON without any markdown formatting."""

    user_prompt = f"""Analyze this contract and extract the following information in JSON format:

{{
  "title": "The main title of the agreement",
  "contract_type": "Type (e.g., 'Master Services Agreement', 'NDA', 'Purchase Agreement')",
  "effective_date": "YYYY-MM-DD or null",
  "expiration_date": "YYYY-MM-DD or null", 
  "governing_law": "Jurisdiction (e.g., 'California', 'New York') or null",
  "parties": [
    {{
      "name": "Legal entity name",
      "role": "Vendor/Client/Licensor/Licensee/Partner/etc",
      "address": "Full address if mentioned or null",
      "jurisdiction": "Incorporation jurisdiction or null"
    }}
  ],
  "total_value": {{
    "amount": numeric value or null,
    "currency": "USD/EUR/etc or null",
    "description": "Brief description (e.g., 'Total contract value', 'Annual fee')"
  }},
  "key_dates": [
    {{
      "date": "YYYY-MM-DD",
      "description": "What happens on this date (e.g., 'Payment due', 'Renewal')"
    }}
  ],
  "defined_terms": [
    {{
      "term": "Term name (e.g., 'Deliverables', 'Services')",
      "definition": "Brief definition text"
    }}
  ]
}}

Contract (first 4000 characters):
{markdown_content[:4000]}

Return ONLY valid JSON."""

    result = call_llm(system_prompt, user_prompt)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            print(f"  ⚠ JSON parse error: {e}")
    
    # Fallback to basic extraction
    parts = filename.replace(".md", "").split("_")
    return {
        "title": " ".join(parts[2:]) if len(parts) > 2 else filename,
        "contract_type": parts[2] if len(parts) > 2 else "Unknown",
        "effective_date": None,
        "expiration_date": None,
        "governing_law": None,
        "parties": [],
        "total_value": None,
        "key_dates": [],
        "defined_terms": []
    }


def segment_clauses(markdown_content: str) -> list[dict[str, Any]]:
    """Segment markdown into clauses based on headers."""
    clauses = []
    lines = markdown_content.split('\n')
    
    current_section = None
    current_title = None
    current_content = []
    position = 0
    
    for line in lines:
        if line.startswith('##'):
            # Save previous clause
            if current_content:
                text = '\n'.join(current_content).strip()
                if text and len(text) > 50:
                    clauses.append({
                        "section_label": current_section,
                        "title": current_title,
                        "text_content": text,
                        "position": position
                    })
                    position += 1
            
            # Start new clause
            header_text = line.lstrip('#').strip()
            if current_section:
                current_section = f"{current_section} / {header_text}"
            else:
                current_section = header_text
            current_title = header_text
            current_content = []
        else:
            current_content.append(line)
    
    # Save final clause
    if current_content:
        text = '\n'.join(current_content).strip()
        if text and len(text) > 50:
            clauses.append({
                "section_label": current_section,
                "title": current_title,
                "text_content": text,
                "position": position
            })
    
    return clauses


def classify_and_analyze_clause(clause_text: str, clause_title: str) -> dict[str, Any]:
    """Comprehensive clause analysis using LLM."""
    
    system_prompt = """You are a legal contract analyzer. Classify clauses accurately and identify risks, obligations, rights, and monetary values. Return ONLY valid JSON."""

    user_prompt = f"""Analyze this contract clause:

Title: {clause_title}
Text: {clause_text[:2000]}

Return JSON with:
{{
  "clause_type": "One of: Definitions, Indemnification, Limitation of Liability, Confidentiality, Intellectual Property, Termination, Payment Terms, Warranties, Data Protection, Force Majeure, Dispute Resolution, Service Level Agreement, Change Management, Acceptance Criteria, Insurance, Other",
  "risk_level": "low/medium/high",
  "is_standard": true/false,
  "risk_rationale": "Explanation if medium/high risk",
  "obligations": [
    {{
      "description": "What must be done",
      "responsible_party": "Who must do it (extract from text or 'Vendor'/'Client')",
      "beneficiary_party": "Who benefits (or null)",
      "due_date_description": "When (e.g., 'within 30 days') or null",
      "penalty_description": "Consequence of non-compliance or null",
      "is_high_impact": true/false
    }}
  ],
  "rights": [
    {{
      "description": "What can be done",
      "holder_party": "Who holds the right",
      "condition_description": "Under what conditions or null",
      "expiration_description": "When it expires or null"
    }}
  ],
  "monetary_values": [
    {{
      "amount": numeric value or null,
      "currency": "USD/EUR or null",
      "value_type": "Fee/Cap/Penalty/etc",
      "context": "Brief description",
      "multiple_of_fees": numeric multiplier or null
    }}
  ],
  "conditions": [
    {{
      "description": "Condition that triggers something",
      "trigger_event": "What triggers it"
    }}
  ]
}}

Return ONLY valid JSON."""

    result = call_llm(system_prompt, user_prompt, temperature=0.1)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            pass
    
    # Fallback to basic classification
    return {
        "clause_type": "Other",
        "risk_level": "low",
        "is_standard": True,
        "risk_rationale": None,
        "obligations": [],
        "rights": [],
        "monetary_values": [],
        "conditions": []
    }


def ingest_contract_comprehensive(filepath: Path):
    """Comprehensive contract ingestion with rich ontology. Each call uses its own connection."""
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
        
        # Create contract identifier
        contract_id_parts = filepath.stem.split('_')
        contract_identifier = f"{contract_id_parts[0]}_{contract_id_parts[1]}" if len(contract_id_parts) >= 2 else filepath.stem
        
        # Insert contract
        cur.execute("""
            INSERT INTO contracts (contract_identifier, title, contract_type, effective_date, 
                                expiration_date, governing_law, source_file_path, source_markdown)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (contract_identifier) DO UPDATE 
            SET title = EXCLUDED.title, updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            contract_identifier,
            metadata.get("title", filepath.stem),
            metadata.get("contract_type"),
            metadata.get("effective_date"),
            metadata.get("expiration_date"),
            metadata.get("governing_law"),
            str(filepath),
            markdown_content
        ))
        
        contract_id = cur.fetchone()['id']
        conn.commit()
        print(f"  ✓ Contract created (ID: {contract_id})")
        
        # Insert jurisdiction if governing_law specified
        jurisdiction_id = None
        if metadata.get("governing_law"):
            cur.execute("""
                INSERT INTO jurisdictions (name, country, state_province)
                VALUES (%s, %s, %s)
                ON CONFLICT (name, country, state_province) DO UPDATE 
                SET name = EXCLUDED.name
                RETURNING id
            """, (metadata["governing_law"], None, None))
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
            
            party_jurisdiction_id = None
            if party_info.get("jurisdiction"):
                cur.execute("""
                    INSERT INTO jurisdictions (name, country, state_province)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name, country, state_province) DO UPDATE 
                    SET name = EXCLUDED.name
                    RETURNING id
                """, (party_info["jurisdiction"], None, None))
                party_jurisdiction_id = cur.fetchone()['id']
            
            cur.execute("""
                INSERT INTO parties (name, party_type, address, jurisdiction_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (tenant_id, name) DO UPDATE 
                SET address = EXCLUDED.address, updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (party_name, "Corporation", party_info.get("address"), party_jurisdiction_id))
            
            party_id = cur.fetchone()['id']
            party_map[party_name] = party_id
            
            # Link party to contract
            party_role = party_info.get("role", "Unknown")
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
        
        print("  🧠 Analyzing clauses with LLM (this may take a while)...")
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
                    cur.execute("""
                        INSERT INTO monetary_values (contract_id, clause_id, amount, currency, 
                                                value_type, context, multiple_of_fees)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        contract_id,
                        clause_id,
                        monetary["amount"],
                        monetary.get("currency", "USD"),
                        monetary.get("value_type"),
                        monetary.get("context"),
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
        return (filepath.name, False, str(e))


def prepare_graphrag_input():
    """Prepare contract files for GraphRAG ingestion by converting to text format."""
    print("\n[*] Preparing GraphRAG input files...")
    graphrag_input_dir = Path("data/input")
    
    contract_files = sorted(graphrag_input_dir.glob("contract_*.md"))
    print(f"  [OK] Found {len(contract_files)} contract files ready for GraphRAG")
    return len(contract_files)


def run_graphrag_indexing():
    """Run GraphRAG indexing pipeline using the CLI."""
    import subprocess
    import shutil
    
    print("\n[*] Running Microsoft GraphRAG indexing...")
    print("  This will create knowledge graph with entities, relationships, and communities...")
    
    try:
        # Run graphrag index command
        result = subprocess.run(
            ["graphrag", "index", "--root", ".", "--config", "graphrag_config"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        # Show stdout for debugging
        if result.stdout:
            print(f"  GraphRAG output:\n{result.stdout[:1000]}")
        
        if result.returncode == 0:
            print("  [OK] GraphRAG indexing complete")
            
            # Move output from root 'output/' to 'data/output/' for consistency
            root_output = Path("output")
            target_output = Path("data/output")
            
            if root_output.exists():
                print("  📦 Moving GraphRAG output to data/output/...")
                
                # Create target directory if it doesn't exist
                target_output.mkdir(parents=True, exist_ok=True)
                
                # Move artifacts directory
                if (root_output / "artifacts").exists():
                    if (target_output / "artifacts").exists():
                        shutil.rmtree(target_output / "artifacts")
                    shutil.move(str(root_output / "artifacts"), str(target_output / "artifacts"))
                    print("    ✓ Moved artifacts/")
                
                # Move lancedb directory
                if (root_output / "lancedb").exists():
                    if (target_output / "lancedb").exists():
                        shutil.rmtree(target_output / "lancedb")
                    shutil.move(str(root_output / "lancedb"), str(target_output / "lancedb"))
                    print("    [OK] Moved lancedb/")
                
                # Clean up empty root output directory
                if root_output.exists() and not any(root_output.iterdir()):
                    root_output.rmdir()
                    print("    [OK] Cleaned up root output/")
            
            return True
        else:
            print(f"  [!] GraphRAG indexing had issues:")
            print(f"    {result.stderr[:500]}")
            return False
    except FileNotFoundError:
        print("  [!] GraphRAG CLI not found. Install with: pip install graphrag")
        return False
    except Exception as e:
        print(f"  [!] GraphRAG indexing error: {e}")
        return False


def main():
    """Main comprehensive ingestion pipeline - Dual PostgreSQL + GraphRAG."""
    print("=" * 70)
    print("Contract Intelligence - Hybrid Ingestion Pipeline")
    print("PostgreSQL (Structured) + Microsoft GraphRAG (Knowledge Graph)")
    print("=" * 70)
    
    if not DB_PASSWORD:
        print("[X] ERROR: POSTGRES_ADMIN_PASSWORD not set")
        return
    
    if not openai_client.api_key:
        print("[X] ERROR: GRAPHRAG_API_KEY not set")
        return
    
    # Test database connection
    print("\n[*] Testing PostgreSQL connection...")
    try:
        test_conn = get_db_connection()
        test_cur = test_conn.cursor()
        test_cur.execute("SELECT version();")
        print("[OK] Connected")
        test_cur.close()
        test_conn.close()
    except Exception as e:
        print(f"[X] Connection failed: {e}")
        return
    
    # Initialize schema (using separate connection)
    print("\n[*] Initializing PostgreSQL schema...")
    schema_file = Path("backend/schema.sql")
    if schema_file.exists():
        conn = get_db_connection()
        cur = conn.cursor()
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        cur.execute(schema_sql)
        conn.commit()
        cur.close()
        conn.close()
        print("[OK] Schema initialized")
    else:
        print("[!] Schema file not found, skipping...")
    
    # Find contract files
    contract_files = sorted(INPUT_DIR.glob("contract_*.md"))
    print(f"\n[*] Found {len(contract_files)} contract files")
    
    # Process ALL contracts (not just first 5)
    num_to_process = len(contract_files)
    n_parallel = 5
    print(f"\n[*] Processing ALL {num_to_process} contracts into PostgreSQL with {n_parallel} parallel workers...")
    
    successful = 0
    failed = 0
    failed_files = []
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=n_parallel) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_single_contract, filepath): filepath 
            for filepath in contract_files  # Process ALL contracts
        }
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_file):
            filename, success, message = future.result()
            
            if success:
                successful += 1
                print(f"  [OK] {filename} - {message}")
            else:
                failed += 1
                failed_files.append((filename, message))
                print(f"  [X] {filename} - {message}")
    
    # Show any failures
    if failed_files:
        print(f"\n[!] Failed contracts:")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")
    
    # Summary statistics
    print("\n" + "=" * 70)
    print(f"[OK] PostgreSQL Ingestion complete: {successful} successful, {failed} failed")
    print("=" * 70)
    
    # Get final PostgreSQL statistics
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as cnt FROM contracts")
    contract_count = cur.fetchone()['cnt']
    
    cur.execute("SELECT COUNT(*) as cnt FROM clauses")
    clause_count = cur.fetchone()['cnt']
    
    cur.execute("SELECT COUNT(*) as cnt FROM obligations")
    obligation_count = cur.fetchone()['cnt']
    
    cur.execute("SELECT COUNT(*) as cnt FROM rights")
    right_count = cur.fetchone()['cnt']
    
    cur.execute("SELECT COUNT(*) as cnt FROM monetary_values")
    monetary_count = cur.fetchone()['cnt']
    
    cur.execute("SELECT COUNT(*) as cnt FROM risks")
    risk_count = cur.fetchone()['cnt']
    
    cur.execute("SELECT COUNT(*) as cnt FROM term_definitions")
    term_count = cur.fetchone()['cnt']
    
    print(f"\n[*] PostgreSQL Database Statistics:")
    print(f"  Contracts: {contract_count}")
    print(f"  Clauses: {clause_count}")
    print(f"  Obligations: {obligation_count}")
    print(f"  Rights: {right_count}")
    print(f"  Monetary Values: {monetary_count}")
    print(f"  Risks: {risk_count}")
    print(f"  Defined Terms: {term_count}")
    
    cur.close()
    conn.close()
    
    # Now run GraphRAG indexing
    print("\n" + "=" * 70)
    print("Phase 2: Microsoft GraphRAG Knowledge Graph Creation")
    print("=" * 70)
    
    graphrag_count = prepare_graphrag_input()
    graphrag_success = run_graphrag_indexing()
    
    # Final summary
    print("\n" + "=" * 70)
    print("[*] HYBRID INGESTION COMPLETE")
    print("=" * 70)
    print(f"[OK] PostgreSQL: {successful}/{num_to_process} contracts")
    print(f"[OK] GraphRAG: {'Success' if graphrag_success else 'Partial/Failed'} ({graphrag_count} files)")
    print("\nYou now have:")
    print("  1. Structured SQL data in PostgreSQL (precise queries)")
    print("  2. Knowledge graph in GraphRAG (community detection, global search)")
    print("=" * 70)


if __name__ == "__main__":
    main()
