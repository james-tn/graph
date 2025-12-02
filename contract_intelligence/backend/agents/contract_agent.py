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
GRAPHRAG_API_KEY = os.environ.get("GRAPHRAG_API_KEY")
GRAPHRAG_API_BASE = os.environ.get("GRAPHRAG_API_BASE")

if not GRAPHRAG_API_KEY:
    raise ValueError("GRAPHRAG_API_KEY environment variable is required")
if not GRAPHRAG_API_BASE:
    raise ValueError("GRAPHRAG_API_BASE environment variable is required")

# OpenAI client for embeddings
openai_client = OpenAI(
    api_key=GRAPHRAG_API_KEY,
    base_url=GRAPHRAG_API_BASE + "/openai/v1/" if not GRAPHRAG_API_BASE.endswith("/") else GRAPHRAG_API_BASE + "openai/v1/"
)

EMBEDDING_MODEL = os.environ.get("GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small")

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
    - Semantic search using pgvector distance operators (<->, <=>)
    
    For semantic search with embeddings:
    - Use %s placeholder in ORDER BY clause: ORDER BY cl.embedding <=> %s LIMIT 20
    - Set need_embedding=True and provide search_text
    - The embedding vector will be automatically bound to %s
    
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
           1 - (cl.embedding <=> %s) as similarity
    FROM clauses cl
    JOIN contracts c ON cl.contract_id = c.id
    ORDER BY cl.embedding <=> %s
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
            # Count %s placeholders in query
            param_count = sql_query.count('%s')
            params = tuple([embedding_vector] * param_count) if param_count > 0 else None
        
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
        api_key = os.getenv("GRAPHRAG_API_KEY")
        if not api_key:
            raise ValueError("GRAPHRAG_API_KEY environment variable is required")
        
        self.agent = ChatAgent(
            chat_client=AzureOpenAIResponsesClient(api_key=api_key),
            instructions="""You are a Contract Intelligence Assistant with PostgreSQL + Apache AGE graph database access.

## DATABASE SCHEMA

### Core Tables

**contracts** - Contract documents
- id, contract_identifier (unique), reference_number (e.g., MSA-ABC-202401-005)
- title, contract_type (see types below)
- effective_date, expiration_date, status ('active', 'expired', 'terminated')
- governing_law, jurisdiction_id → jurisdictions

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
Nodes: Contract, Clause, Party, Obligation, Right
Edges: IS_PARTY_TO, CONTAINS_CLAUSE, IMPOSES_OBLIGATION, GRANTS_RIGHT, HOLDS_RIGHT

## WHEN TO USE WHICH CAPABILITY

**Use plain SQL for:**
- Simple filters and aggregations on contracts, clauses, risks, parties, monetary_values tables
- Straightforward JOINs (e.g., contracts ↔ parties_contracts ↔ parties)
- Counting, summing, grouping by fields
- Example: "How many active contracts do we have?" or "List all high-risk clauses"

**Use Cypher via Apache AGE for:**
- Multi-hop patterns spanning several entity types (Party → Contract → Clause → Risk/Obligation/Right)
- Questions clearly about "paths" or "connections" across the graph
- Complex relationship queries like "Which parties are connected to high-risk obligations through multiple contracts?"
- Example: "Show me all paths from Acme Corp through contracts to high-risk clauses"

**Use semantic search (embedding) when:**
- User asks about "clauses similar to..." or "find language that talks about..."
- Question is conceptual, not about named clause types
- Need to match meaning/intent, not exact keywords
- Example: "Find clauses about data breach notification" (matches various phrasings)

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
-- Find clauses similar to a concept
SELECT 
  c.reference_number,
  cl.section_label,
  cl.title,
  cl.text_content,
  1 - (cl.embedding <=> %s) as similarity
FROM clauses cl
JOIN contracts c ON cl.contract_id = c.id
ORDER BY cl.embedding <=> %s
LIMIT 20
```
**IMPORTANT:** Set need_embedding=True and search_text="liability cap exceptions"

### 5. Apache AGE Cypher - Multi-Hop Graph Patterns

**CRITICAL Cypher Format:**
```sql
-- Set search path for AGE
SET search_path = ag_catalog, '$user', public;

-- Query format: SELECT * FROM cypher('graph_name', $$ CYPHER_QUERY $$) AS (col1 agtype, col2 agtype, ...)
SELECT * FROM cypher('contract_intelligence', $$
  MATCH (p:Party)-[r1:IS_PARTY_TO]->(c:Contract)-[r2:CONTAINS_CLAUSE]->(cl:Clause)
  WHERE p.name =~ '.*Acme.*'
  RETURN p.name, c.reference_number, c.title, cl.section_label, cl.risk_level
  LIMIT 20
$$) as (party_name agtype, contract_ref agtype, contract_title agtype, clause_section agtype, risk_level agtype)
```

**MUST wrap Cypher in cypher() function and declare ALL return columns with agtype!**

```sql
-- Multi-hop: Party → Contract → Clause → Obligation
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)-[:IMPOSES_OBLIGATION]->(o:Obligation)
  WHERE cl.risk_level = 'high'
  RETURN p.name, c.reference_number, cl.section_label, o.description
  LIMIT 20
$$) as (party agtype, contract agtype, clause agtype, obligation agtype)
```

```sql
-- Find paths between parties through contracts
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('contract_intelligence', $$
  MATCH path = (p1:Party)-[:IS_PARTY_TO]->(:Contract)<-[:IS_PARTY_TO]-(p2:Party)
  WHERE p1.name =~ '.*Acme.*' AND p2.name =~ '.*TechCorp.*'
  RETURN p1.name, p2.name, length(path) as hops
  LIMIT 10
$$) as (party1 agtype, party2 agtype, hops agtype)
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
✅ **Use ILIKE** for case-insensitive string matching (e.g., `WHERE name ILIKE '%acme%'`)
✅ **Include relationship_type** when querying contract_relationships
✅ **For Cypher:** SET search_path first, wrap in cypher(), declare ALL columns with agtype
✅ **Complex questions:** Break into multiple focused queries, combine results
✅ **Choose the right tool:** SQL for simple queries, recursive SQL for hierarchies, Cypher for multi-hop patterns

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
