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
from agent_framework import ChatAgent

# Load environment variables from .env file
load_dotenv()
from agent_framework.azure import AzureOpenAIResponsesClient
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
        
        self.agent = ChatAgent(
            chat_client=AzureOpenAIResponsesClient(api_key=api_key),
            instructions="""You are a Contract Intelligence Assistant with PostgreSQL + Apache AGE graph database access.

## DATABASE SCHEMA

### Core Tables

**contracts** - Contract documents
- id, contract_identifier (unique, e.g., 'contract_197'), reference_number (business ref, e.g., 'MSA-ABC-202401-005', can be NULL)
- title, contract_type (see types below)
- effective_date, expiration_date, status ('active', 'expired', 'terminated')
- governing_law, jurisdiction_id → jurisdictions
- Note: Graph nodes use `identifier` property which maps to SQL `contract_identifier`

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

**Filtering & Matching:**
- Case-insensitive regex: `p.name =~ '(?i).*acme.*'` or `c.title =~ '(?i).*master.*'`
- Exact matches: `WHERE c.status = 'active'`, `WHERE cl.risk_level = 'high'`, `WHERE c.type = 'Master Services Agreement'`
- Property existence: `WHERE EXISTS(c.expiration_date)` or `WHERE c.penalty IS NOT NULL`
- Multiple conditions: `WHERE c.status = 'active' AND c.type = 'Statement of Work'`
- Access in RETURN: `RETURN p.name, c.identifier, c.type, cl.risk_level`

## WHEN TO USE WHICH CAPABILITY

**Use plain SQL for:**
- Simple filters and aggregations on contracts, clauses, risks, parties, monetary_values tables
- Straightforward JOINs (e.g., contracts ↔ parties_contracts ↔ parties)
- Counting, summing, grouping by fields
- Example: "How many active contracts do we have?" or "List all high-risk clauses"

**Use Cypher via Apache AGE for:**
- **Contract hierarchies**: MSA → SOWs, amendments, work orders (use relationship direction child → parent!)
- Multi-hop patterns spanning several entity types (Party → Contract → Clause → Risk/Obligation/Right)
- Questions about "all children" or "parent contracts" or "family tree"
- Questions clearly about "paths" or "connections" across the graph
- Complex relationship queries like "Which parties are connected to high-risk obligations through multiple contracts?"
- Example: "Show me all SOWs under this MSA" → Use Cypher with `(sow)-[:SOW_OF]->(msa)`
- Example: "Show me all paths from Acme Corp through contracts to high-risk clauses"

**Use semantic search (embedding) when:**
- User asks about "clauses similar to..." or "find language that talks about..."
- Question is conceptual, not about named clause types
- Need to match meaning/intent, not exact keywords
- Looking for "clauses about X" where X is a concept (liability, indemnification, termination rights, etc.)
- Want to find similar contractual language across different contracts
- Example: "Find clauses about data breach notification" (matches various phrasings)
- Example: "Show clauses similar to indemnification in Acme contracts"
- Example: "What clauses discuss intellectual property ownership?"

**Semantic Search Best Practices:**
- Keep search_text focused on the concept (e.g., "liability cap exceptions" not "find clauses with...")
- Use 1 - (embedding <=> %s::vector) for similarity score (0-1 range, higher = more similar)
- Combine with SQL filters: `WHERE c.contract_type = 'MSA' AND similarity > 0.7`
- Typical similarity thresholds: >0.8 = very similar, >0.6 = related, <0.5 = different

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
-- Find SOWs under a specific MSA (include relationship_type!)
SELECT 
  child.reference_number, 
  child.title, 
  child.contract_type,
  cr.relationship_type,
  cr.relationship_description
FROM contract_relationships cr
JOIN contracts child ON cr.child_contract_id = child.id
JOIN contracts parent ON cr.parent_contract_id = parent.id
WHERE parent.reference_number = 'MSA-ABC-202401-005'
  AND cr.relationship_type = 'sow'
LIMIT 20
```

### 3. Recursive SQL - Contract Families

```sql
-- Complete contract family tree
WITH RECURSIVE tree AS (
  SELECT 
    id, 
    reference_number, 
    title, 
    contract_type,
    0 as level,
    ARRAY[reference_number] as path
  FROM contracts 
  WHERE reference_number = 'MSA-ABC-202401-005'
  
  UNION ALL
  
  SELECT 
    c.id, 
    c.reference_number, 
    c.title,
    c.contract_type,
    t.level + 1,
    t.path || c.reference_number
  FROM contracts c
  JOIN contract_relationships cr ON c.id = cr.child_contract_id
  JOIN tree t ON cr.parent_contract_id = t.id
  WHERE t.level < 5
)
SELECT 
  level,
  reference_number, 
  title,
  contract_type,
  array_to_string(path, ' → ') as hierarchy
FROM tree 
ORDER BY level, reference_number 
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
  WHERE p1.name =~ '(?i).*acme.*' AND p2.name =~ '(?i).*techcorp.*'
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

✅ **VISUALIZE FIRST:** Always ask "Can I show this as a chart?" before writing text
✅ **BE CONCISE:** 2-3 sentences max, then show a chart
✅ **ALWAYS use LIMIT** (20-50 rows) to prevent overwhelming responses
✅ **Use ILIKE or regex** for case-insensitive matching: SQL `ILIKE '%acme%'`, Cypher `=~ '(?i).*acme.*'`
✅ **Include relationship_type** when querying contract_relationships table
✅ **For Cypher:** SET search_path first, wrap in cypher(), declare ALL columns with agtype
✅ **⚠️ Contract hierarchies in Cypher:** ALWAYS use child → parent direction: `(sow)-[:SOW_OF]->(msa)` NOT `(msa)-[:SOW_OF]->(sow)`
✅ **Complex questions:** Break into multiple focused queries, combine results
✅ **Choose the right tool:** SQL for simple queries, recursive SQL for hierarchies, Cypher for multi-hop patterns and contract families
✅ **Verify queries:** For contract hierarchies, double-check relationship direction matches child → parent
✅ **Filter by status:** Remember to add `WHERE c.status = 'active'` when counting active contracts

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
        self.thread = self.agent.get_new_thread()
    
    async def query_async(self, query_text: str) -> dict:
        """Execute a query asynchronously."""
        result = await self.agent.run(query_text, thread=self.thread)
        
        # Extract SQL queries and their reasoning from tool calls in the conversation
        tool_calls = []
        
        for message in result.messages:
            
            # Extract reasoning (text content) that comes before tool calls
            reasoning = ""
            current_tool_calls = []
            
            for content in message.contents:
                # Handle text content
                if hasattr(content, 'text'):
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
        "Show me statistics about our contract portfolio including relationship counts",
        "Analyze the complete contract family tree for Zenith Technologies Master Services Agreement MSA-ZEN-202403-197",
        "What are all the obligations and rights for Acme Corp in their contracts?",
        "Find all high-risk liability clauses in contracts with Phoenix Industries",
        "Show me all amendments to the Data Processing Agreement DPA-SUM-202502-324",
        "List all Statement of Work contracts under the Phoenix Industries Master Agreement MSA-PHO-202508-344",
        "Find data processing and confidentiality clauses similar to Nova Systems contracts using semantic search",
        "What contracts with Atlas Ventures have auto-renewal clauses and what are the notice periods?",
        "Show the contract hierarchy for the Pinnacle Services Data Processing Agreement DPA-PIN-202411-069"
    ]
    
    for query in queries:
        print(f"\n{'─' * 70}")
        print(f"User: {query}")
        print(f"{'─' * 70}")
        
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("The agent dynamically wrote and executed SQL/Cypher queries")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
