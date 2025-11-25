#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Contract Ingestion Pipeline

Loads contract markdown files from data/input, extracts metadata and clauses,
uses Azure OpenAI to classify and analyze content, then stores in PostgreSQL
with embeddings and full-text search vectors.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg2
from openai import OpenAI
from psycopg2.extras import RealDictCursor

# Configuration
DB_HOST = "ci-ci-dev-pgflex.postgres.database.azure.com"
DB_NAME = "cipgraph"
DB_USER = "pgadmin"
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")
INPUT_DIR = Path("data/input")

# OpenAI client for embeddings and classification
openai_client = OpenAI(
    api_key=os.environ.get("GRAPHRAG_API_KEY"),
    base_url=os.environ.get("GRAPHRAG_API_BASE") + "/openai/v1/"
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
        sslmode='require'
    )


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for text using Azure OpenAI."""
    response = openai_client.embeddings.create(
        input=text[:8000],  # Truncate to avoid token limits
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def extract_contract_metadata(markdown_content: str, filename: str) -> dict[str, Any]:
    """Extract contract metadata using LLM."""
    prompt = f"""Analyze this contract and extract the following information in JSON format:
- title: The main title of the agreement
- contract_type: Type of agreement (e.g., "Purchase Agreement", "NDA", "MSA", "Consulting Agreement")
- effective_date: Effective date (format: YYYY-MM-DD, or null if not found)
- expiration_date: Expiration/termination date (format: YYYY-MM-DD, or null if not found)
- parties: List of party names and their roles (array of {{"name": "...", "role": "..."}})
- governing_law: Governing law jurisdiction (e.g., "California", "New York", or null)

Contract excerpt (first 3000 characters):
{markdown_content[:3000]}

Return ONLY valid JSON without any markdown formatting or explanation."""

    try:
        response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a legal contract analyzer. Extract structured data and return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        
        return json.loads(result.strip())
    
    except Exception as e:
        print(f"  ⚠ Error extracting metadata: {e}")
        # Return minimal metadata from filename
        parts = filename.replace(".md", "").split("_")
        return {
            "title": " ".join(parts[2:]) if len(parts) > 2 else filename,
            "contract_type": parts[2] if len(parts) > 2 else "Unknown",
            "effective_date": None,
            "expiration_date": None,
            "parties": [],
            "governing_law": None
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
        # Check for markdown headers
        if line.startswith('##'):
            # Save previous clause if exists
            if current_content:
                text = '\n'.join(current_content).strip()
                if text and len(text) > 50:  # Minimum clause length
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


def classify_clause(clause_text: str, clause_title: str) -> dict[str, Any]:
    """Classify clause type and risk level using simple heuristics."""
    # Simple keyword-based classification for faster testing
    text_lower = f"{clause_title} {clause_text}".lower()
    
    clause_type = "Other"
    risk_level = "low"
    is_standard = True
    risk_rationale = None
    
    # Classify by keywords
    if any(word in text_lower for word in ["definition", "defined term", "means"]):
        clause_type = "Definitions"
    elif any(word in text_lower for word in ["indemnif", "hold harmless"]):
        clause_type = "Indemnification"
        risk_level = "medium"
        is_standard = False
    elif any(word in text_lower for word in ["limitation of liability", "liability cap"]):
        clause_type = "Limitation of Liability"
        risk_level = "high" if "unlimited" in text_lower or "uncapped" in text_lower else "medium"
        is_standard = False
        if risk_level == "high":
            risk_rationale = "Potentially unlimited liability exposure"
    elif any(word in text_lower for word in ["confidential", "non-disclosure", "proprietary"]):
        clause_type = "Confidentiality"
    elif any(word in text_lower for word in ["intellectual property", "ip rights", "patent", "copyright"]):
        clause_type = "Intellectual Property"
        risk_level = "medium"
    elif any(word in text_lower for word in ["terminat", "cancel"]):
        clause_type = "Termination"
    elif any(word in text_lower for word in ["payment", "fee", "invoice", "compensation"]):
        clause_type = "Payment Terms"
    elif any(word in text_lower for word in ["warrant", "represent"]):
        clause_type = "Warranties"
    elif any(word in text_lower for word in ["data protection", "privacy", "gdpr", "personal data"]):
        clause_type = "Data Protection"
        risk_level = "medium"
    elif any(word in text_lower for word in ["force majeure", "act of god"]):
        clause_type = "Force Majeure"
    elif any(word in text_lower for word in ["dispute", "arbitration", "litigation"]):
        clause_type = "Dispute Resolution"
    elif any(word in text_lower for word in ["service level", "sla", "uptime"]):
        clause_type = "Service Level Agreement"
        risk_level = "medium"
    
    return {
        "clause_type": clause_type,
        "risk_level": risk_level,
        "is_standard": is_standard,
        "risk_rationale": risk_rationale
    }


def ingest_contract(filepath: Path, conn, cur):
    """Ingest a single contract file."""
    print(f"\n📄 Processing: {filepath.name}")
    
    # Read markdown content
    with open(filepath, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Extract metadata
    print("  🔍 Extracting metadata...")
    metadata = extract_contract_metadata(markdown_content, filepath.name)
    
    # Create contract identifier from filename
    contract_id_parts = filepath.stem.split('_')
    contract_identifier = f"{contract_id_parts[0]}_{contract_id_parts[1]}" if len(contract_id_parts) >= 2 else filepath.stem
    
    # Insert contract
    cur.execute("""
        INSERT INTO contracts (contract_identifier, title, contract_type, effective_date, 
                             expiration_date, governing_law, source_file_path, source_markdown)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (contract_identifier) DO UPDATE 
        SET title = EXCLUDED.title,
            updated_at = CURRENT_TIMESTAMP
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
    
    contract_id = cur.fetchone()[0]
    conn.commit()
    print(f"  ✓ Contract created (ID: {contract_id})")
    
    # Insert parties
    parties_data = metadata.get("parties", [])
    for party_info in parties_data:
        party_name = party_info.get("name")
        party_role = party_info.get("role", "Unknown")
        
        if party_name:
            # Insert party
            cur.execute("""
                INSERT INTO parties (name, party_type)
                VALUES (%s, %s)
                ON CONFLICT (tenant_id, name) DO UPDATE 
                SET updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (party_name, "Corporation"))
            
            party_id = cur.fetchone()[0]
            
            # Get role_id
            cur.execute("SELECT id FROM party_roles WHERE name = %s", (party_role,))
            role_row = cur.fetchone()
            role_id = role_row[0] if role_row else None
            
            # Link party to contract
            cur.execute("""
                INSERT INTO parties_contracts (party_id, contract_id, role_id, role_description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (party_id, contract_id, role_id) DO NOTHING
            """, (party_id, contract_id, role_id, party_role))
    
    conn.commit()
    print(f"  ✓ Parties linked: {len(parties_data)}")
    
    # Segment and process clauses
    print("  📝 Segmenting clauses...")
    clauses_data = segment_clauses(markdown_content)
    print(f"  ✓ Found {len(clauses_data)} clauses")
    
    clause_count = 0
    for i, clause_data in enumerate(clauses_data):
        if i % 5 == 0:
            print(f"    Processing clause {i+1}/{len(clauses_data)}...")
        
        # Classify clause
        classification = classify_clause(clause_data["text_content"], clause_data.get("title", ""))
        
        # Get clause_type_id
        cur.execute("SELECT id FROM clause_types WHERE name = %s", (classification["clause_type"],))
        clause_type_row = cur.fetchone()
        clause_type_id = clause_type_row[0] if clause_type_row else None
        
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
            classification["risk_level"],
            classification["is_standard"],
            clause_data["text_content"],
            embedding,
            clause_data["position"]
        ))
        
        clause_id = cur.fetchone()[0]
        
        # If high risk, create risk entry
        if classification["risk_level"] in ["high", "medium"] and classification.get("risk_rationale"):
            cur.execute("""
                INSERT INTO risks (contract_id, clause_id, risk_type_custom, risk_level, rationale, detected_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                contract_id,
                clause_id,
                classification["clause_type"],
                classification["risk_level"],
                classification["risk_rationale"],
                "LLM Classification"
            ))
        
        clause_count += 1
        
        # Commit every 10 clauses
        if clause_count % 10 == 0:
            conn.commit()
    
    conn.commit()
    print(f"  ✓ Clauses processed: {clause_count}")
    
    return contract_id


def main():
    """Main ingestion pipeline."""
    print("=" * 70)
    print("Contract Intelligence - Data Ingestion Pipeline")
    print("=" * 70)
    
    # Check environment
    if not DB_PASSWORD:
        print("❌ ERROR: POSTGRES_ADMIN_PASSWORD not set")
        return
    
    if not openai_client.api_key:
        print("❌ ERROR: GRAPHRAG_API_KEY not set")
        return
    
    # Connect to database
    print("\n🔌 Connecting to PostgreSQL...")
    conn = get_db_connection()
    cur = conn.cursor()
    print("✓ Connected")
    
    # Initialize schema
    print("\n📋 Initializing schema...")
    schema_file = Path("backend/schema.sql")
    if schema_file.exists():
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        cur.execute(schema_sql)
        conn.commit()
        print("✓ Schema initialized")
    else:
        print("⚠ Schema file not found, assuming schema exists")
    
    # Find contract files
    contract_files = sorted(INPUT_DIR.glob("contract_*.md"))
    print(f"\n📂 Found {len(contract_files)} contract files")
    
    # Process contracts
    successful = 0
    failed = 0
    
    for filepath in contract_files[:5]:  # Process first 5 for testing
        try:
            ingest_contract(filepath, conn, cur)
            successful += 1
        except Exception as e:
            print(f"  ❌ Error processing {filepath.name}: {e}")
            failed += 1
            conn.rollback()
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✓ Ingestion complete: {successful} successful, {failed} failed")
    print("=" * 70)
    
    # Show statistics
    cur.execute("SELECT COUNT(*) FROM contracts")
    contract_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM clauses")
    clause_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM risks")
    risk_count = cur.fetchone()[0]
    
    print(f"\n📊 Database Statistics:")
    print(f"  Contracts: {contract_count}")
    print(f"  Clauses: {clause_count}")
    print(f"  Risks: {risk_count}")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
