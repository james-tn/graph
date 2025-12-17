# 📥 Data Ingestion Pipeline

> **Comprehensive documentation for the Contract Intelligence PostgreSQL ingestion system**

This module handles the extraction, transformation, and loading of contract data into PostgreSQL with Apache AGE graph support.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Pipeline Flow](#pipeline-flow)
- [Scripts Reference](#scripts-reference)
- [Entity Resolution](#entity-resolution)
- [Database Schema](#database-schema)
- [Usage](#usage)
- [Configuration](#configuration)

---

## Overview

The data ingestion pipeline transforms markdown contract documents into a rich, queryable PostgreSQL database with:

- **Structured relational data** (contracts, parties, clauses, obligations, rights)
- **Vector embeddings** for semantic search (pgvector, 1536 dimensions)
- **Graph relationships** for multi-hop traversal (Apache AGE)
- **Full-text search** with trigram similarity (pg_trgm)
- **Entity resolution** to deduplicate parties across contracts

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────────────┘

   data/input/*.md                    PostgreSQL + Apache AGE
   ┌──────────────┐                   ┌────────────────────────────────────┐
   │ contract_001 │                   │  contracts         │  clauses      │
   │ contract_002 │  ──────────────►  │  parties           │  obligations  │
   │ contract_... │   LLM Extraction  │  jurisdictions     │  rights       │
   │ contract_700 │                   │  relationships     │  risks        │
   └──────────────┘                   └────────────────────────────────────┘
                                                   │
                                                   ▼
                                      ┌────────────────────────────────────┐
                                      │        Apache AGE Graph            │
                                      │  :Contract ─[:CONTAINS]─► :Clause  │
                                      │  :Party ◄─[:IS_PARTY_TO]─ :Contract│
                                      │  :Clause ─[:IMPOSES]─► :Obligation │
                                      └────────────────────────────────────┘
```

---

## Pipeline Flow

The ingestion process follows this sequence:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: INITIALIZATION                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  • test_connection()          → Validate PostgreSQL connection              │
│  • initialize_schema()        → Execute schema.sql (DROP + CREATE tables)   │
│  • Glob contract_*.md files   → Find all input files in data/input/        │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: PARALLEL CONTRACT PROCESSING                                       │
│  process_contracts() with ThreadPoolExecutor                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  For each contract file (N parallel workers):                               │
│     └──► ingest_contract_comprehensive(filepath)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: LLM-POWERED EXTRACTION (contract_extractor.py)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ 3a. extract_contract_metadata(markdown, filename)                     │ │
│  │     • Uses Azure OpenAI with Pydantic structured outputs              │ │
│  │     • Extracts: title, type, dates, parties[], governing_law,         │ │
│  │       defined_terms[], total_value, parent_contract_reference         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ 3b. segment_clauses(markdown)                                         │ │
│  │     • Splits contract into individual clauses via LLM                 │ │
│  │     • Returns: section_label, title, text_content, position           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ 3c. For each clause → classify_and_analyze_clause()                   │ │
│  │     • Classifies clause_type (16 predefined types)                    │ │
│  │     • Extracts: risk_level, obligations[], rights[],                  │ │
│  │       monetary_values[], conditions[]                                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ 3d. get_embedding(clause_text)                                        │ │
│  │     • Generates 1536-dim vector using text-embedding-3-small          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: DATABASE INSERTIONS (with Entity Resolution)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │   contracts    │  │  jurisdictions │  │    parties     │                │
│  │ ON CONFLICT    │  │ ON CONFLICT    │  │ + Fuzzy Match  │                │
│  │ (identifier)   │  │ (name,country) │  │ (pg_trgm 0.8)  │                │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                │
│          │                   │                   │                          │
│          ▼                   ▼                   ▼                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │ contract_      │  │ term_          │  │    clauses     │◄── embedding   │
│  │ relationships  │  │ definitions    │  │                │                │
│  └────────────────┘  └────────────────┘  └───────┬────────┘                │
│                                                  │                          │
│        ┌─────────────────────────────────────────┼────────────┐            │
│        ▼                    ▼                    ▼            ▼            │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐  ┌────────────┐   │
│  │ obligations│      │   rights   │      │ monetary_  │  │   risks    │   │
│  │            │      │            │      │ values     │  │            │   │
│  └────────────┘      └────────────┘      └────────────┘  └────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: POST-PROCESSING                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  • resolve_orphaned_relationships() → Link child→parent contracts           │
│  • explore_data.py                  → Generate data exploration report      │
│  • build_graph.py                   → Create Apache AGE graph nodes/edges   │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: APACHE AGE GRAPH CONSTRUCTION (build_graph.py)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   NODE TYPES                              EDGE TYPES                        │
│  ┌────────────────┐                      ┌─────────────────────────────┐   │
│  │ :Contract      │──IS_PARTY_TO───────►│ :Party                      │   │
│  │ :Clause        │──CONTAINS_CLAUSE───►│ :Clause                     │   │
│  │ :Obligation    │──IMPOSES_OBLIGATION►│ :Obligation                 │   │
│  │ :Right         │──GRANTS_RIGHT──────►│ :Right                      │   │
│  │ :Term          │──AMENDS────────────►│ :Contract (parent)          │   │
│  │ :Risk          │──DEFINES_TERM──────►│ :Term                       │   │
│  └────────────────┘                      └─────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| **postgres_ingestion.py** | Main ingestion entry point | `python postgres_ingestion.py` |
| **ingestion_pipeline.py** | Unified pipeline (PostgreSQL + GraphRAG) | `python ingestion_pipeline.py` |
| **contract_extractor.py** | LLM extraction logic (metadata, clauses) | Imported by postgres_ingestion |
| **build_graph.py** | Apache AGE graph construction | `python build_graph.py` |
| **schema.sql** | Database schema definition | Executed by initialize_schema() |
| **explore_data.py** | Data exploration and reporting | `python explore_data.py` |
| **check_relationships.py** | Diagnostic: verify graph relationships | `python check_relationships.py` |

---

## Entity Resolution

The pipeline includes a two-layer entity resolution system to prevent duplicate party records:

### Layer 1: Name Normalization

Before storing, party names are normalized to a canonical form:

```python
# Example transformations:
"Acme Corporation, Inc."  →  "acme corporation"
"CONTOSO CORP."           →  "contoso"
"Summit Tech, LLC"        →  "summit tech"
```

**Normalization rules:**
- Convert to lowercase
- Strip 25+ legal suffixes (Inc., LLC, Corp., Ltd., GmbH, etc.)
- Remove punctuation and special characters
- Normalize whitespace

### Layer 2: Fuzzy Matching (pg_trgm)

Before inserting a new party, the system checks for similar existing parties:

```sql
SELECT id, name, similarity(canonical_name, 'contoso enterprises') as sim
FROM parties
WHERE similarity(canonical_name, 'contoso enterprises') > 0.8
ORDER BY sim DESC
LIMIT 1;
```

**Matching behavior:**
- Similarity threshold: **0.8** (configurable)
- If match found: reuse existing `party_id`
- If no match: insert new party
- Fuzzy matches are logged: `🔗 Entity resolved: 'Acme Corp.' → 'Acme Corporation' (similarity: 0.85)`

### Deduplication Summary

| Entity | Dedup Key | Strategy |
|--------|-----------|----------|
| **contracts** | `contract_identifier` | `ON CONFLICT DO UPDATE` |
| **jurisdictions** | `(name, country, state_province)` | `ON CONFLICT DO UPDATE` |
| **parties** | `canonical_name` + fuzzy match | pg_trgm similarity > 0.8 |
| **parties_contracts** | `(party_id, contract_id, role_id)` | `ON CONFLICT DO NOTHING` |
| **term_definitions** | `(contract_id, term_name)` | `ON CONFLICT DO NOTHING` |
| **contract_relationships** | `(child_id, parent_id, type)` | `ON CONFLICT DO NOTHING` |

---

## Database Schema

The schema is defined in `schema.sql` and includes:

### Core Tables

```
contracts                 # Contract metadata and full text
├── clauses              # Individual contract sections with embeddings
│   ├── obligations      # Party obligations extracted from clauses
│   ├── rights           # Party rights extracted from clauses
│   ├── monetary_values  # Financial terms (amounts, currencies)
│   └── risks            # Risk assessments per clause
├── parties              # Companies/individuals (deduplicated)
├── parties_contracts    # Many-to-many with roles
├── contract_relationships  # Parent-child hierarchies (MSA→SOW→Amendment)
├── term_definitions     # Defined terms per contract
└── jurisdictions        # Legal jurisdictions
```

### Extensions Required

```sql
CREATE EXTENSION IF NOT EXISTS vector;    -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS age;       -- Apache AGE for graph
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- Trigram similarity
```

### Key Indexes

- `idx_clauses_embedding` - HNSW index for vector similarity search
- `idx_clauses_fulltext` - GIN index for full-text search
- `idx_parties_canonical_trgm` - Trigram index for fuzzy party matching

---

## Usage

### Quick Start

```bash
# Navigate to data_ingestion directory
cd contract_intelligence/data_ingestion

# Run interactive ingestion
python postgres_ingestion.py

# Options:
#   1 = Quick test (1 contract)
#   5 = Moderate test (5 contracts)
#   20 = Medium batch (20 contracts)
#   a = Full ingestion (all contracts)
```

### Programmatic Usage

```python
from postgres_ingestion import run_postgres_ingestion

# Full ingestion with defaults
run_postgres_ingestion()

# Partial ingestion, skip schema init
run_postgres_ingestion(
    num_contracts=10,
    n_parallel=5,
    skip_schema_init=True  # Preserve existing data
)
```

### Unified Pipeline (PostgreSQL + GraphRAG)

```bash
python ingestion_pipeline.py
```

This runs both:
1. PostgreSQL ingestion with Apache AGE graph
2. GraphRAG knowledge graph indexing

---

## Configuration

### Environment Variables

Create a `.env` file in the `contract_intelligence` directory:

```bash
# PostgreSQL
POSTGRES_HOST=your-server.postgres.database.azure.com
POSTGRES_DATABASE=cipgraph
POSTGRES_USER=pgadmin
POSTGRES_ADMIN_PASSWORD=your-password

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small
```

### Tuning Parameters

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| `SIMILARITY_THRESHOLD` | postgres_ingestion.py | 0.8 | Fuzzy match threshold for parties |
| `n_parallel` | run_postgres_ingestion() | 8 | Parallel worker count |
| `LLM_MODEL` | contract_extractor.py | gpt-4.1 | Model for extraction |
| `EMBEDDING_MODEL` | contract_extractor.py | text-embedding-3-small | Model for embeddings |

---

## Troubleshooting

### Common Issues

**1. "pg_trgm extension not found"**
```sql
-- Run as superuser
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

**2. "Apache AGE not installed"**
```sql
-- Requires Azure PostgreSQL Flexible Server with AGE enabled
CREATE EXTENSION IF NOT EXISTS age;
```

**3. "value too long for type character varying"**
- The schema includes generous VARCHAR limits
- If exceeded, values are auto-truncated with logging

**4. "Parent contract not found"**
- Child contracts ingested before parents create orphaned relationships
- `resolve_orphaned_relationships()` runs automatically at the end
- Parent references are stored and resolved when parent is ingested

### Diagnostic Commands

```bash
# Check database statistics
python -c "from postgres_ingestion import get_database_statistics; print(get_database_statistics())"

# Verify graph relationships
python check_relationships.py

# Explore ingested data
python explore_data.py
```

---

## Related Documentation

- [Main Project README](../README.md) - Full platform documentation
- [Backend API](../backend/README.md) - API endpoints and agents
- [GraphRAG Config](../graphrag_config/README.md) - Microsoft GraphRAG setup
