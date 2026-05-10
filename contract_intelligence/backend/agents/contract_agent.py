#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Contract Intelligence PostgreSQL Agent with Graph Traversal

AI agent that can query the contract database using:
- SQL for analytics and aggregations
- Vector search for semantic similarity
- Full-text search for keyword matching
- Apache AGE graph traversal for multi-hop reasoning
"""

import asyncio
import os
from typing import Annotated

import psycopg2
from dotenv import load_dotenv

from agent_framework import Agent

# Load environment variables from .env file
load_dotenv()
from agent_framework.openai import OpenAIChatClient
from azure.identity import AzureCliCredential
from openai import OpenAI
from pydantic import Field
from psycopg2.extras import RealDictCursor

# Database configuration from environment variables
DB_HOST = os.environ.get("POSTGRES_HOST", "ci-ci-dev-pgflex.postgres.database.azure.com")
DB_NAME = os.environ.get("POSTGRES_DATABASE", "cipgraph")
DB_USER = os.environ.get("POSTGRES_USER", "pgadmin")
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")
GRAPH_NAME = "contract_intelligence"

# Validate required environment variables
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")

if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")

# OpenAI client for embeddings
openai_client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_ENDPOINT 
)

EMBEDDING_MODEL = os.environ.get("EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small")

def get_db_connection():
    """Create a database connection with timeout settings."""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require',
            cursor_factory=RealDictCursor,
            connect_timeout=30,  # 30 second connection timeout
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
    except psycopg2.OperationalError as e:
        print(f"[ERROR] PostgreSQL connection failed: {e}")
        raise Exception(f"Database connection timeout or unavailable: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Unexpected database error: {e}")
        raise


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for text."""
    response = openai_client.embeddings.create(
        input=text[:8000],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def execute_sql_query(
    sql_query: Annotated[str, Field(description="""SQL query to execute. Can include:
    - Standard SQL (SELECT, JOIN, WHERE, GROUP BY, aggregations)
    - CTEs with WITH and WITH RECURSIVE for hierarchical queries
    - Apache AGE graph queries using cypher() function
    - Semantic search using pgvector distance operators
    
    For semantic search with embeddings:
    - Use <=> operator (cosine distance) for similarity: ORDER BY embedding <=> %s::vector
    - IMPORTANT: Must cast %s placeholder to ::vector type
    - Set need_embedding=True and provide search_text
    - The embedding will be passed as string '[x,y,z,...]' and bound to %s placeholder
    
    For graph traversal with Apache AGE:
    - Use: SELECT * FROM cypher('contract_intelligence', $$ MATCH ... RETURN ... $$) as (col1 agtype, col2 agtype, ...)
    - Example: SELECT * FROM cypher('contract_intelligence', $$
        MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)
        WHERE p.name =~ '.*Acme.*'
        RETURN p.name, c.title
        LIMIT 20
      $$) as (party_name agtype, contract_title agtype)
    - Must include column aliases with agtype for each returned value
    """)],
    need_embedding: Annotated[bool, Field(description="Set True if query uses semantic search with %s placeholder for embedding vector")] = False,
    search_text: Annotated[str | None, Field(description="Text to embed for semantic search (only when need_embedding=True)")] = None
) -> str:
    """Execute a SQL query against the PostgreSQL database.
    
    This single tool handles ALL query types:
    1. **Standard SQL**: JOINs, WHERE clauses, aggregations, filtering
    2. **Semantic Search**: pgvector similarity with %s placeholder
    3. **Graph Traversal**: Apache AGE cypher() function for relationships
    
    SEMANTIC SEARCH EXAMPLE:
    ```sql
    SELECT c.contract_identifier, cl.section_label, cl.text_content,
           1 - (cl.embedding <=> %s::vector) as similarity
    FROM clauses cl
    JOIN contracts c ON cl.contract_id = c.id
    ORDER BY cl.embedding <=> %s::vector
    LIMIT 20
    ```
    Call with: need_embedding=True, search_text="liability limitations"
    
    GRAPH TRAVERSAL EXAMPLE:
    ```sql
    SELECT * FROM cypher('contract_intelligence', $$
      MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)-[:IMPOSES_OBLIGATION]->(o:Obligation)
      WHERE p.name =~ '.*Acme.*'
      RETURN p.name, c.title, o.description
      LIMIT 20
    $$) as (party_name agtype, contract_title agtype, obligation_desc agtype)
    ```
    
    IMPORTANT:
    - Only SELECT queries allowed (no INSERT/UPDATE/DELETE)
    - Always use LIMIT (recommended: 20-50)
    - For cypher(), must set search_path first (handled automatically)
    - Use agtype for all cypher() return column types
    """
    try:
        # Validate it's a read-only query
        query_upper = sql_query.strip().upper()
        
        # Allow SELECT and WITH (for CTEs including WITH RECURSIVE)
        if not (query_upper.startswith('SELECT') or query_upper.startswith('WITH')):
            return "Error: Only SELECT queries and CTEs (WITH) are allowed for security reasons."
        
        # Check for dangerous keywords
        dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']
        if any(keyword in query_upper for keyword in dangerous):
            return f"Error: Query contains forbidden operations: {', '.join([k for k in dangerous if k in query_upper])}"
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # If query uses cypher(), set search_path for Apache AGE
        if 'CYPHER(' in query_upper:
            cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Generate embedding if needed
        params = None
        if need_embedding:
            if not search_text:
                return "Error: search_text required when need_embedding=True"
            embedding_vector = get_embedding(search_text)
            # Convert to string format for pgvector: '[x,y,z,...]'
            embedding_str = '[' + ','.join(map(str, embedding_vector)) + ']'
            # Count %s placeholders in query
            param_count = sql_query.count('%s')
            params = tuple([embedding_str] * param_count) if param_count > 0 else None
        
        # Execute query
        if params:
            cur.execute(sql_query, params)
        else:
            cur.execute(sql_query)
        
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return "Query executed successfully but returned no results."
        
        # Format results as table
        if len(results) > 0:
            columns = results[0].keys()
            response = f"Found {len(results)} result(s):\n\n"
            
            # Create simple table
            for row in results[:50]:  # Limit display to 50 rows
                for col in columns:
                    value = row[col]
                    # Format value nicely
                    if isinstance(value, str) and len(value) > 200:
                        value = value[:200] + "..."
                    response += f"{col}: {value}\n"
                response += "\n"
            
            if len(results) > 50:
                response += f"\n... and {len(results) - 50} more results (truncated for display)"
            
            return response
        
        return "Query executed successfully."
    
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return f"Database Connection Timeout: The query took too long to execute or the database is unavailable.\n\nError: {error_msg}\n\nQuery was: {sql_query[:200]}..."
        return f"Database Connection Error: {error_msg}\n\nQuery was: {sql_query[:200]}..."
    except psycopg2.Error as e:
        return f"PostgreSQL Error: {str(e)}\n\nQuery was: {sql_query[:200]}..."
    except Exception as e:
        return f"Unexpected Error: {str(e)}\n\nQuery was: {sql_query[:200]}..."



class ContractAgent:
    """Schema-aware PostgreSQL agent that writes and executes SQL/Cypher queries."""
    
    def __init__(self):
        """Initialize the contract agent."""
        # Get API key from environment
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-5.4")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        # OpenAIChatClient (azure_endpoint mode) expects the base endpoint without /openai/v1/ suffix
        endpoint = endpoint.rstrip("/").removesuffix("/openai/v1").removesuffix("/openai")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
        
        self.agent = Agent(
            # agent-framework 1.3.0+: AzureOpenAIChatClient was unified into OpenAIChatClient.
            # Pass azure_endpoint to opt into the Azure OpenAI variant.
            client=OpenAIChatClient(
                model=deployment_name,
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=api_version,
            ),
            instructions="""You are a Contract Intelligence Assistant with PostgreSQL + Apache AGE graph database access.

## DATABASE SCHEMA

### Core Tables

**contracts** - Contract documents
- id, contract_identifier (unique, e.g., 'contract_197'), reference_number (business ref, e.g., 'MSA-ZEN-202403-197', can be NULL)
- title, contract_type (see types below)
- effective_date, expiration_date, status ('active', 'expired', 'terminated')
- governing_law, jurisdiction_id → jurisdictions

⚠️ **CRITICAL IDENTIFIER MAPPING:**
- SQL `contract_identifier` (e.g., 'contract_197') = Graph `c.identifier`
- SQL `reference_number` (e.g., 'MSA-ZEN-202403-197') = **SQL-ONLY, NOT in graph**
- When user mentions a reference_number like 'MSA-ZEN-202403-197', FIRST look up the contract_identifier via SQL:
  `SELECT contract_identifier FROM contracts WHERE reference_number = 'MSA-ZEN-202403-197'`
  Then use that identifier (e.g., 'contract_197') in Cypher queries.

**contract_relationships** - Contract hierarchies (MSA → SOWs, amendments, etc.)
- child_contract_id → contracts, parent_contract_id → contracts
- parent_reference_number (captured even if parent not ingested)
- relationship_type: 'amendment', 'sow', 'addendum', 'work_order', 'maintenance', 'related'
- relationship_description

**clauses** - Contract sections
- contract_id → contracts, clause_type_id → clause_types
- section_label, title, text_content
- risk_level: 'low', 'medium', 'high'
- embedding vector(1536) - for semantic search
- full_text_vector tsvector - for keyword search

**parties** - Organizations and individuals
- name, party_type, address, jurisdiction_id → jurisdictions

**parties_contracts** - Party-contract relationships
- party_id → parties, contract_id → contracts
- role_id → party_roles, role_description

**obligations** - Contractual obligations
- clause_id → clauses, description
- responsible_party_id → parties, beneficiary_party_id → parties
- due_date, penalty_description, is_high_impact

**rights** - Contractual rights
- clause_id → clauses, description
- holder_party_id → parties, condition_description, expiration_date

**monetary_values** - Financial amounts
- contract_id → contracts, clause_id → clauses
- amount, currency (ISO codes: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR)
- value_type, context

**risks** - Identified risks
- contract_id → contracts, clause_id → clauses
- risk_type_id → risk_types, risk_level ('low', 'medium', 'high')
- rationale, is_confirmed

### Lookup Tables with Values

**clause_types**: Definitions, Indemnification, Limitation of Liability, Confidentiality, Intellectual Property, Termination, Payment Terms, Warranties, Data Protection, Force Majeure, Dispute Resolution, Service Level Agreement, Change Management, Acceptance Criteria, Insurance, Other

**party_roles**: Client, Vendor, Licensor, Licensee, Consultant, Partner, Employer, Employee, Landlord, Tenant

**risk_types**: Uncapped Liability, Unlimited Indemnity, Auto-Renewal, Unilateral Modification, Data Sovereignty, Weak Termination Rights, Intellectual Property Transfer, Broad NDA Scope, Payment Terms, Regulatory Compliance

**contract_types** (common values): Master Services Agreement, Statement of Work, Amendment, Addendum, Service Agreement, NDA, Purchase Agreement, Employment Agreement, Lease Agreement, License Agreement, Data Processing Agreement, Consulting Agreement, Other

### Apache AGE Graph
Graph: `contract_intelligence`

**Node Types** (all have `db_id` property linking to PostgreSQL primary key):
- **Contract**: db_id, identifier, title, type, status, effective_date, expiration_date, governing_law, jurisdiction
- **Party**: db_id, name, type, address, jurisdiction
- **Clause**: db_id, contract_db_id, section, title, type, risk_level, is_standard, position
- **Obligation**: db_id, clause_db_id, description, responsible_party_db_id, beneficiary_party_db_id, penalty, is_high_impact
- **Right**: db_id, clause_db_id, description, holder_party_db_id, condition
- **Term**: db_id, contract_db_id, name, definition
- **MonetaryValue**: db_id, contract_db_id, clause_db_id, amount, currency, value_type, context, multiple_of_fees
- **Risk**: db_id, contract_db_id, clause_db_id, risk_type, risk_level, rationale, detected_by
- **Condition**: db_id, description, trigger_event

**Relationship Types** (edges):
- **IS_PARTY_TO**: Party → Contract (links parties to contracts)
- **CONTAINS_CLAUSE**: Contract → Clause (contract sections)
- **IMPOSES_OBLIGATION**: Clause → Obligation (contractual duties)
- **RESPONSIBLE_FOR**: Party → Obligation (who must perform)
- **GRANTS_RIGHT**: Clause → Right (contractual entitlements)
- **HOLDS_RIGHT**: Party → Right (who holds the right)
- **DEFINES_TERM**: Contract → Term (defined terms at contract level)
- **HAS_VALUE**: Contract/Clause → MonetaryValue (financial amounts)
- **HAS_RISK**: Contract/Clause → Risk (identified risks)

**CRITICAL - Contract Hierarchy Relationships (ALL point Child → Parent):**
- **AMENDS**: Amendment → OriginalContract (e.g., Amendment-001 → MSA-100)
- **SOW_OF**: StatementOfWork → MasterAgreement (e.g., SOW-200 → MSA-197)
- **ADDENDUM_TO**: Addendum → Contract (e.g., Addendum-A → MSA-100)
- **WORK_ORDER_OF**: WorkOrder → ParentContract (e.g., WO-150 → MSA-148)
- **MAINTENANCE_OF**: MaintenanceAgreement → ParentContract
- **RELATED_TO**: Contract → Contract (generic relationships)

⚠️ **COMMON MISTAKE**: Do NOT write `(msa)-[:SOW_OF]->(sow)` - this is BACKWARDS!
✓ **CORRECT**: `(sow:Contract)-[:SOW_OF]->(msa:Contract)` (child points to parent)

**Key Properties for Cypher Queries:**
- Use `db_id` to match nodes with PostgreSQL data (e.g., `c.db_id`, `p.db_id`)
- **Contract properties**: `c.identifier` (contract_identifier in SQL), `c.type` (contract_type in SQL), `c.status`, `c.title`, `c.effective_date`, `c.expiration_date`, `c.governing_law`
- **Party properties**: `p.name`, `p.type` (party_type in SQL), `p.address`, `p.jurisdiction`
- **Clause properties**: `cl.section` (section_label in SQL), `cl.type` (clause_type in SQL), `cl.risk_level`, `cl.title`, `cl.is_standard`, `cl.position`
- **Obligation properties**: `o.description`, `o.penalty`, `o.is_high_impact`
- **Risk properties**: `r.risk_type`, `r.risk_level`, `r.rationale`
- **Term properties**: `t.name`, `t.definition`
- **MonetaryValue properties**: `m.amount`, `m.currency`, `m.value_type`

**Filtering & Matching in Cypher:**
- **Case-insensitive regex**: `WHERE p.name =~ '(?i).*acme.*'` or `WHERE c.title =~ '(?i).*master.*'`
- **Substring matching**: `WHERE p.name CONTAINS 'Zenith'` or `WHERE c.title CONTAINS 'Master'`
- **Starts with**: `WHERE c.identifier STARTS WITH 'contract_1'`
- **Exact matches**: `WHERE c.status = 'active'`, `WHERE cl.risk_level = 'high'`, `WHERE c.type = 'Master Services Agreement'`
- **Identifier lookup**: `WHERE c.identifier = 'contract_197'` (NOT reference_number!)
- **Multiple conditions**: `WHERE c.status = 'active' AND c.type = 'Statement of Work'`
- **Access in RETURN**: `RETURN p.name, c.identifier, c.type, cl.risk_level`

## QUERY ROUTING — DECISION TREE

Follow this decision tree **in order** to choose the right query method.

### Step 1: Is the user asking about meaning/concept, not structure?
- "clauses **similar to**...", "find language that **talks about**...", "clauses **about** X"
- The question is conceptual — no specific clause type, party name, or field to filter
- → **USE SEMANTIC SEARCH** (set `need_embedding=True`, provide `search_text`)

### Step 2: Does the question involve traversing relationships of unknown/variable depth?
Look for these signals:
- "**family tree**", "**all children**", "**all SOWs under**", "**hierarchy**"
- "**connected to**", "**paths between**", "**related through**"
- "Party → Contract → Clause → Obligation" (3+ hops across different node types)
- "What **amendments** and **work orders** sit under this MSA?" (multiple edge types)
- → **USE CYPHER** (Apache AGE graph query)

### Step 3: Everything else → USE SQL
- Counting, summing, averaging, ranking (`COUNT`, `SUM`, `GROUP BY`, `ORDER BY`)
- Filtering on typed columns (`WHERE status = 'active'`, `WHERE amount > 1000000`)
- Date ranges (`WHERE expiration_date BETWEEN ...`)
- Fixed 1-2 hop JOINs you know in advance (contracts → parties, clauses → clause_types)
- Cross-tabulations (risk_level × governing_law)
- → **USE PLAIN SQL**

### Hybrid Patterns (use BOTH)
Some questions need two steps:
1. **SQL first** to look up identifiers, then **Cypher** for traversal:
   - User says "MSA-ZEN-202403-197" → SQL: `SELECT contract_identifier FROM contracts WHERE reference_number = 'MSA-ZEN-202403-197'` → gets `contract_197` → Cypher: `MATCH (parent:Contract {identifier: 'contract_197'})<-[r]-(child:Contract)`
2. **Cypher first** for discovery, then **SQL** for aggregation:
   - "Total value of all contracts under Zenith MSA" → Cypher to find children → SQL to SUM monetary values

### Quick Reference Table

| Signal in question | Method | Why |
|---|---|---|
| count, total, sum, average, rank, top N | **SQL** | Aggregation on typed fields |
| expiring, date range, before/after | **SQL** | Date arithmetic |
| amount > X, currency, value | **SQL** | Numeric comparison |
| by vendor, by type, by jurisdiction | **SQL** | GROUP BY on structured columns |
| family tree, hierarchy, children under | **Cypher** | Variable-depth traversal |
| connected to, paths between, related through | **Cypher** | Graph pattern matching |
| Party → Contract → Clause → Obligation | **Cypher** | Multi-hop (3+ entity types) |
| SOWs, amendments, work orders under MSA | **Cypher** | Multiple edge types (SOW_OF, AMENDS, WORK_ORDER_OF) |
| similar to, language about, clauses discussing | **Semantic** | Meaning matching via embeddings |
| find clauses like, conceptually related | **Semantic** | Cosine similarity search |

### ⚠️ Common Mistakes to Avoid
- ❌ Do NOT use `WITH RECURSIVE` SQL for contract hierarchies → use Cypher instead (simpler, faster)
- ❌ Do NOT use Cypher for simple counts like "how many contracts?" → use SQL `SELECT COUNT(*)`
- ❌ Do NOT use Cypher to look up a single contract by reference_number → use SQL `WHERE reference_number = '...'`
- ❌ Do NOT use semantic search when the user names a specific clause type (e.g., "Termination clauses") → use SQL `WHERE clause_type = 'Termination'`

### Semantic Search Best Practices
- Keep `search_text` focused on the concept (e.g., `"liability cap exceptions"` not `"find clauses with..."`)
- Use `1 - (embedding <=> %s::vector)` for similarity score (0-1 range, higher = more similar)
- Combine with SQL filters: `WHERE c.contract_type = 'MSA'` + embedding search
- Typical thresholds: >0.8 = very similar, >0.6 = related, <0.5 = different

## QUERY TOOL

**execute_sql_query(sql_query, need_embedding=False, search_text=None)**
- For standard SQLand Cypher queries
- Set need_embedding=True and search_text="..." for semantic search
- Returns query results



## QUERY PATTERNS

### 1. Standard SQL - Simple Filters & Aggregations

```sql
-- Count contracts by type
SELECT contract_type, COUNT(*) as count
FROM contracts
WHERE status = 'active'
GROUP BY contract_type
ORDER BY count DESC LIMIT 20
```

```sql
-- High-risk clauses with contract info
SELECT c.reference_number, c.title, cl.clause_type_id, cl.title as clause_title
FROM clauses cl
JOIN contracts c ON cl.contract_id = c.id
WHERE cl.risk_level = 'high'
LIMIT 20
```

### 2. Contract Relationships - Standard Joins

```sql
-- Find SOWs under a specific MSA (via SQL joins)
SELECT 
  child.contract_identifier,
  child.reference_number, 
  child.title, 
  child.contract_type,
  cr.relationship_type,
  cr.relationship_description
FROM contract_relationships cr
JOIN contracts child ON cr.child_contract_id = child.id
JOIN contracts parent ON cr.parent_contract_id = parent.id
WHERE parent.contract_identifier = 'contract_197'
  AND cr.relationship_type = 'sow'
LIMIT 20
```

### 3. Recursive SQL - Contract Families

```sql
-- Complete contract family tree (via SQL recursive CTE)
WITH RECURSIVE tree AS (
  SELECT 
    id, 
    contract_identifier,
    reference_number, 
    title, 
    contract_type,
    0 as level,
    ARRAY[contract_identifier] as path
  FROM contracts 
  WHERE contract_identifier = 'contract_197'
  
  UNION ALL
  
  SELECT 
    c.id, 
    c.contract_identifier,
    c.reference_number, 
    c.title,
    c.contract_type,
    t.level + 1,
    t.path || c.contract_identifier
  FROM contracts c
  JOIN contract_relationships cr ON c.id = cr.child_contract_id
  JOIN tree t ON cr.parent_contract_id = t.id
  WHERE t.level < 5
)
SELECT 
  level,
  contract_identifier,
  reference_number, 
  title,
  contract_type,
  array_to_string(path, ' → ') as hierarchy
FROM tree 
ORDER BY level, contract_identifier 
LIMIT 50
```

### 4. Semantic Search - Conceptual Matching

```sql
-- Find clauses semantically similar to a concept (using cosine distance)
SELECT 
  c.contract_identifier,
  cl.section_label,
  cl.title,
  cl.text_content,
  1 - (cl.embedding <=> %s::vector) as similarity_score
FROM clauses cl
JOIN contracts c ON cl.contract_id = c.id
ORDER BY cl.embedding <=> %s::vector
LIMIT 20
```
**IMPORTANT:** 
- Set need_embedding=True and search_text="liability cap exceptions"
- MUST cast %s to ::vector type (cosine distance: 0 = identical, 2 = opposite)

### 5. Apache AGE Cypher - Multi-Hop Graph Patterns

**CRITICAL Cypher Format:**
```sql
-- Set search path for AGE
SET search_path = ag_catalog, '$user', public;

-- Query format: SELECT * FROM cypher('graph_name', $$ CYPHER_QUERY $$) AS (col1 agtype, col2 agtype, ...)
SELECT * FROM cypher('contract_intelligence', $$
  MATCH (p:Party)-[r1:IS_PARTY_TO]->(c:Contract)-[r2:CONTAINS_CLAUSE]->(cl:Clause)
  WHERE p.name =~ '(?i).*acme.*'
  RETURN p.name, c.identifier, c.title, cl.section, cl.risk_level
  LIMIT 20
$$) as (party_name agtype, contract_id agtype, contract_title agtype, clause_section agtype, risk_level agtype)
```

**MUST wrap Cypher in cypher() function and declare ALL return columns with agtype!**

```sql
-- Multi-hop: Party → Contract → Clause → Obligation
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)-[:IMPOSES_OBLIGATION]->(o:Obligation)
  WHERE cl.risk_level = 'high'
  RETURN p.name, c.identifier, cl.section, o.description
  LIMIT 20
$$) as (party agtype, contract_id agtype, clause_section agtype, obligation agtype)
```

```sql
-- Find paths between parties through contracts
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH path = (p1:Party)-[:IS_PARTY_TO]->(:Contract)<-[:IS_PARTY_TO]-(p2:Party)
  WHERE p1.name =~ '(?i).*acme.*' AND p2.name =~ '(?i).*zenith.*'
  RETURN p1.name, p2.name, length(path) as hops
  LIMIT 10
$$) as (party1 agtype, party2 agtype, hops agtype)
```

**⚠️ CONTRACT HIERARCHY QUERIES - CRITICAL DIRECTION:**

```sql
-- CORRECT: Find all SOWs under an MSA (child → parent direction)
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH (sow:Contract)-[:SOW_OF]->(msa:Contract)
  WHERE msa.identifier = 'contract_197'
    AND sow.type = 'Statement of Work'
    AND sow.status = 'active'
  RETURN sow.identifier, sow.title, sow.status, msa.identifier, msa.title
  LIMIT 20
$$) as (sow_id agtype, sow_title agtype, sow_status agtype, msa_id agtype, msa_title agtype)
```

```sql
-- Count active SOWs under each MSA (CORRECT direction)
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH (sow:Contract)-[:SOW_OF]->(msa:Contract)
  WHERE msa.type = 'Master Services Agreement'
    AND sow.type = 'Statement of Work'
    AND sow.status = 'active'
  WITH msa, COUNT(sow) AS active_sow_count
  RETURN msa.identifier, msa.title, active_sow_count
  ORDER BY active_sow_count DESC
  LIMIT 50
$$) as (msa_id agtype, msa_title agtype, sow_count agtype)
```

```sql
-- Complete contract family tree (MSA with all children)
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH (parent:Contract)<-[r]-(child:Contract)
  WHERE parent.identifier = 'contract_197'
  RETURN child.identifier, child.type, child.title, type(r) as relationship, parent.identifier
  LIMIT 50
$$) as (child_id agtype, child_type agtype, child_title agtype, rel_type agtype, parent_id agtype)
```

```sql
-- Find all amendments to a contract (amendment → original)
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH (amendment:Contract)-[:AMENDS]->(original:Contract)
  WHERE original.identifier = 'contract_324'
  RETURN amendment.identifier, amendment.title, amendment.effective_date, original.title
  ORDER BY amendment.effective_date
  LIMIT 20
$$) as (amd_id agtype, amd_title agtype, amd_date agtype, original_title agtype)
```

```sql
-- Multi-level hierarchy: MSA → SOW → WorkOrder (traverse multiple levels)
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH (wo:Contract)-[:WORK_ORDER_OF]->(sow:Contract)-[:SOW_OF]->(msa:Contract)
  WHERE msa.type = 'Master Services Agreement'
  RETURN msa.identifier, msa.title, sow.identifier, sow.title, wo.identifier, wo.title
  LIMIT 20
$$) as (msa_id agtype, msa_title agtype, sow_id agtype, sow_title agtype, wo_id agtype, wo_title agtype)
```

## OUTPUT FORMATTING

**CRITICAL: Visualize data whenever possible using Mermaid charts! Users prefer graphics over text.**

**Keep responses CONCISE:**
- Use brief bullet points instead of paragraphs
- Let visualizations tell the story
- Include only essential details

**MERMAID SYNTAX RULES (CRITICAL - Follow exactly!):**

⚠️ **NEVER use `<br/>` tags** - Use plain text or `<br>` (without slash) if line break absolutely needed
⚠️ **ALWAYS quote labels with special characters:**
   - Parentheses: `["Pre-Existing IP (Sec. 6.3)"]` NOT `[Pre-Existing IP (Sec. 6.3)]`
   - Commas: `["Vendors (Gamma, Horizon)"]` NOT `[Vendors (Gamma, Horizon)]`
   - Periods: `["Section 6.3. Rights"]` NOT `[Section 6.3. Rights]`
   - Colons, pipes, arrows: Always quote them
⚠️ **Valid node IDs only** - Use alphanumeric, underscore, hyphen (a-z, 0-9, _, -)
⚠️ **XY charts**: Use simple strings in x-axis array, no special chars unquoted

**Examples of CORRECT syntax:**
```mermaid
graph TD
    MSA["MSA-ABC-001 (Master Agreement)"]
    SOW1["SOW-ABC-012 Development Services"]
    MSA --> SOW1
```

```mermaid
xychart-beta
    title "Service Risk Distribution"
    x-axis ["Service Levels", "Hosting", "Support", "Storage"]
    y-axis "Risk Score" 0 --> 100
    bar [75, 60, 45, 30]
```

**Mermaid Chart Types to Use:**

1. **Contract Hierarchies** - Use `graph TD` for family trees:
```mermaid
graph TD
    MSA[MSA-ABC-001<br/>Master Agreement<br/>📋 Active] --> SOW1[SOW-ABC-012<br/>Development Services<br/>📄 Active]
    MSA --> SOW2[SOW-ABC-018<br/>Maintenance<br/>📄 Active]
    MSA --> AMD1[AMD-ABC-025<br/>Amendment 1<br/>📝 Active]
    SOW1 --> WO1[WO-ABC-045<br/>Phase 1 Work Order<br/>📌 Completed]
    style MSA fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    style SOW1 fill:#fff4e6,stroke:#ff9800
    style SOW2 fill:#fff4e6,stroke:#ff9800
    style AMD1 fill:#f3e5f5,stroke:#9c27b0
    style WO1 fill:#e8f5e9,stroke:#4caf50
```

2. **Distributions & Proportions** - Use `pie` charts:
```mermaid
pie title Risk Level Distribution
    "High ⚠️" : 23
    "Medium ⚡" : 45
    "Low ✓" : 32
```

3. **Party Relationships** - Use `graph LR` for networks:
```mermaid
graph LR
    Acme[Acme Corp<br/>Client] -->|MSA-001| B[TechVendor<br/>Vendor]
    Acme -->|NDA-012| C[DataCorp<br/>Partner]
    B -->|SOW-045| D[CloudHost<br/>Subcontractor]
    style Acme fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    style B fill:#fff4e6,stroke:#ff9800
    style C fill:#f3e5f5,stroke:#9c27b0
    style D fill:#e8f5e9,stroke:#4caf50
```

4. **Timelines** - Use `gantt` for date ranges:
```mermaid
gantt
    title Contract Timeline
    dateFormat YYYY-MM-DD
    section Active
    MSA-001 :2024-01-15, 2026-01-15
    SOW-012 :2024-03-01, 2025-03-01
```

5. **Vendor Comparisons** - Use `bar` charts for metrics:
```mermaid
%%{init: {'theme':'dark'}}%%
xychart-beta
    title "Contracts by Vendor"
    x-axis [Acme, TechCorp, DataVendor, CloudProvider]
    y-axis "Contract Count" 0 --> 15
    bar [12, 8, 5, 3]
```

**Text Formatting:**
- Emojis: ⚠️ high, ⚡ medium, ✓ low, 📋 MSA, 📄 SOW, 📝 amendment, 💰 money
- Tables: Use markdown tables ONLY when charts don't work
- Bold key numbers: **$1.2M**, **23 contracts**, **8 high-risk**

## BEST PRACTICES

## BEST PRACTICES

### Query Routing (follow the Decision Tree above!)
✅ **Step 1:** Semantic search for meaning/concept questions
✅ **Step 2:** Cypher for variable-depth traversal and multi-hop patterns
✅ **Step 3:** SQL for everything else (aggregation, filtering, typed fields)
✅ **Hybrid:** SQL to look up identifiers → Cypher for traversal
✅ **Never** use `WITH RECURSIVE` for contract hierarchies — use Cypher instead

### Query Mechanics
✅ **ALWAYS use LIMIT** (20-50 rows) to prevent overwhelming responses
✅ **Text matching:** SQL uses `ILIKE '%acme%'`, Cypher uses `=~ '(?i).*acme.*'` for regex or `CONTAINS 'Acme'` for substring
✅ **For Cypher:** SET search_path first, wrap in cypher(), declare ALL columns with agtype
✅ **Contract hierarchies:** ALWAYS use child → parent direction: `(sow)-[:SOW_OF]->(msa)` NOT the reverse
✅ **Identifier mapping:** reference_number is SQL-only. For Cypher, first look up contract_identifier via SQL
✅ **Complex questions:** Break into multiple focused queries, combine results

### Output
✅ **VISUALIZE FIRST:** Always ask "Can I show this as a chart?" before writing text
✅ **BE CONCISE:** 2-3 sentences max, then show a chart

### Don'ts
❌ **READ-ONLY:** No INSERT/UPDATE/DELETE queries allowed
❌ **Don't compute embeddings:** Use need_embedding=True parameter instead
❌ **Don't forget LIMIT:** Always constrain result size
❌ **Cypher formatting:** Must use exact format shown in examples above
❌ **No long paragraphs:** Use bullets + charts instead""",
            tools=[
                execute_sql_query,
                # get_contract_family,
            ],
        )
        self.thread = self.agent.create_session()
    
    async def query_async(self, query_text: str) -> dict:
        """Execute a query asynchronously."""
        result = await self.agent.run(query_text, session=self.thread)
        
        # Extract SQL queries and their reasoning from tool calls in the conversation
        tool_calls = []
        
        for message in result.messages:
            
            # Extract reasoning (text content) that comes before tool calls
            reasoning = ""
            current_tool_calls = []
            
            for content in message.contents:
                # Handle text content
                if hasattr(content, 'text') and content.text is not None:
                    reasoning += content.text
                
                # Check if this is a function call to execute_sql_query
                if hasattr(content, 'name') and content.name == 'execute_sql_query':
                    args = None
                    # Try parse_arguments method
                    if hasattr(content, 'parse_arguments'):
                        try:
                            args = content.parse_arguments()
                        except:
                            pass
                    # Try arguments attribute
                    if not args and hasattr(content, 'arguments'):
                        try:
                            import json
                            args = json.loads(content.arguments) if isinstance(content.arguments, str) else content.arguments
                        except:
                            pass
                    
                    if args and 'sql_query' in args:
                        current_tool_calls.append({
                            'sql_query': args['sql_query'],
                            'reasoning': reasoning.strip() if reasoning else None,
                            'need_embedding': args.get('need_embedding', False),
                            'search_text': args.get('search_text', None),
                        })
                        reasoning = ""  # Reset reasoning after capturing
            
            # Add tool calls from this message
            tool_calls.extend(current_tool_calls)
        
        print(f"[DEBUG] Total tool calls extracted: {len(tool_calls)}")
        
        return {
            "query": query_text,
            "response": result.text,
            "source": "PostgreSQL with Apache AGE",
            "tool_calls": tool_calls,  # List of tool calls with reasoning and SQL queries
        }
    
    def query(self, query_text: str) -> dict:
        """Execute a query synchronously."""
        return asyncio.run(self.query_async(query_text))


async def main():
    """Main function for the contract intelligence agent."""
    
    print("=" * 70)
    print("Schema-Aware Contract Intelligence Agent")
    print("Dynamically writes SQL and Cypher queries")
    print("=" * 70)
    print()
    
    # Create agent wrapper
    agent_wrapper = ContractAgent()
    agent = agent_wrapper.agent
    thread = agent_wrapper.thread
    
    # Example queries - agent will write SQL/Cypher dynamically
    queries = [
        "How many active contracts do we have, broken down by contract type?",
        "Show the complete contract family tree for Zenith Technologies MSA-ZEN-202403-197",
        "What are all the high-impact obligations for Quantum Labs LLC?",
        "Find all high-risk Termination and Payment Terms clauses with the contract and vendor for each",
        "Show the amendment history for Pinnacle Services DPA-PIN-202411-069",
        "How many active SOWs and work orders sit under each Master Services Agreement?",
        "Find clauses about limitations on liability for indirect or consequential damages using semantic search",
        "Which contracts are expiring in 2026? Show reference number, expiration date, and vendor",
        "What are our largest monetary exposures? Show top 10 by value with vendor name",
    ]
    
    for query in queries:
        print(f"\n{'─' * 70}")
        print(f"User: {query}")
        print(f"{'─' * 70}")
        
        result = await agent.run(query, session=thread)
        print(f"Agent: {result.text}\n")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("The agent dynamically wrote and executed SQL/Cypher queries")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
