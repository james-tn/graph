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

# Database Schema and Ontology
DATABASE_SCHEMA = """
=== PostgreSQL Database Schema ===

TABLES:

1. contracts
   - id (PRIMARY KEY)
   - contract_identifier (VARCHAR(200), UNIQUE) - e.g., 'contract_000_AcmeCorp'
   - reference_number (VARCHAR(200)) - e.g., 'MSA-ABC-202401-005', 'SOW-XYZ-202403-012'
   - title (TEXT)
   - contract_type (VARCHAR(200)) - Values: 'Master Services Agreement', 'Statement of Work', 'Amendment', 'Addendum', 'Service Agreement', 'NDA', etc.
   - effective_date (DATE)
   - expiration_date (DATE)
   - status (VARCHAR(50)) - Values: 'active', 'expired', 'terminated'
   - governing_law (VARCHAR(200))
   - jurisdiction_id (FOREIGN KEY -> jurisdictions.id)
   - source_file_path (TEXT)

2. contract_relationships (NEW - Contract Hierarchies)
   - id (PRIMARY KEY)
   - child_contract_id (FOREIGN KEY -> contracts.id) - The dependent contract
   - parent_contract_id (FOREIGN KEY -> contracts.id) - The master/parent contract
   - parent_reference_number (VARCHAR(200)) - Parent reference even if not yet ingested
   - parent_identifier (VARCHAR(200)) - Parent file identifier
   - relationship_type (TEXT) - Describes relationship: 'Statement of Work under Master Services Agreement', 'Amendment', 'Addendum', 'Work Order', 'Maintenance Agreement', etc.
   - relationship_description (TEXT) - Additional details about the relationship
   - created_at (TIMESTAMP)
   
   IMPORTANT: This table captures contract hierarchies and dependencies:
   - SOWs linked to their Master Service Agreements
   - Amendments linked to original contracts
   - Addenda linked to base documents
   - Work Orders linked to framework agreements

3. clauses
   - id (PRIMARY KEY)
   - contract_id (FOREIGN KEY -> contracts.id)
   - section_label (TEXT) - e.g., 'Section 3.1', 'Article 5'
   - title (TEXT)
   - text_content (TEXT) - Full clause text
   - position_in_contract (INTEGER)
   - clause_type_id (FOREIGN KEY -> clause_types.id)
   - clause_type_custom (TEXT) - Free text if not in clause_types
   - risk_level (TEXT) - Values: 'high', 'medium', 'low', NULL
   - embedding (VECTOR(1536)) - For semantic search
   - full_text_vector (TSVECTOR) - For keyword search

3. parties
   - id (PRIMARY KEY)
   - name (TEXT) - Party name, e.g., 'Acme Corp', 'John Smith'
   - party_type (TEXT) - Values: 'Company', 'Individual', 'Government', etc.

4. parties_contracts (Many-to-many relationship)
   - party_id (FOREIGN KEY -> parties.id)
   - contract_id (FOREIGN KEY -> contracts.id)
   - role_id (FOREIGN KEY -> party_roles.id)
   - role_description (TEXT)

5. party_roles
   - id (PRIMARY KEY)
   - name (TEXT) - Values: 'Vendor', 'Client', 'Employer', 'Employee', 'Lessor', 'Lessee', etc.

6. clause_types
   - id (PRIMARY KEY)
   - name (TEXT) - Values: 'Confidentiality', 'Termination', 'Payment', 'Liability', 'Indemnification', 'IP Rights', etc.

=== Apache AGE Graph Schema ===

Graph Name: contract_intelligence

NODE TYPES:
- Contract: {identifier, title, type, governing_law}
- Clause: {section, title, type, risk_level}
- Party: {name, type}
- Obligation: {description, penalty, is_high_impact}
- Right: {description, condition}

RELATIONSHIP TYPES:
- (Party)-[:IS_PARTY_TO]->(Contract)
- (Contract)-[:CONTAINS_CLAUSE]->(Clause)
- (Clause)-[:IMPOSES_OBLIGATION]->(Obligation)
- (Clause)-[:GRANTS_RIGHT]->(Right)
- (Party)-[:HOLDS_RIGHT]->(Right)

=== Query Capabilities ===

1. SQL Queries:
   - SELECT with JOINs across tables
   - WHERE clauses with ILIKE for case-insensitive pattern matching
   - Aggregations: COUNT, SUM, AVG, GROUP BY
   - Date comparisons and filtering
   - Risk level filtering

2. Semantic Search (Vector Similarity):
   - Use: cl.embedding <=> '[embedding_vector]'::vector
   - Returns similarity score: 1 - (cl.embedding <=> vector)
   - Order by: cl.embedding <=> vector (ascending = most similar)

3. Full-Text Search:
   - Use: cl.full_text_vector @@ plainto_tsquery('english', 'search_term')
   - Ranking: ts_rank(cl.full_text_vector, plainto_tsquery('english', 'term'))

4. Graph Traversal (Apache AGE Cypher):
   - Must set: SET search_path = ag_catalog, '$user', public;
   - Pattern: SELECT * FROM ag_catalog.cypher('contract_intelligence', $$ CYPHER_QUERY $$) as (col1 agtype, col2 agtype, ...);
   - Use MATCH patterns for multi-hop relationships
   - Use WHERE with =~ for regex matching (case-insensitive: '.*term.*')
   - Always LIMIT results (max 50)

=== Common Query Patterns ===

Find contracts by party:
  SELECT c.* FROM contracts c
  JOIN parties_contracts pc ON c.id = pc.contract_id
  JOIN parties p ON pc.party_id = p.id
  WHERE p.name ILIKE '%party_name%'

Find contract relationships (parent-child hierarchy):
  SELECT 
    parent.contract_identifier as parent_contract,
    parent.reference_number as parent_ref,
    child.contract_identifier as child_contract,
    child.reference_number as child_ref,
    cr.relationship_type,
    cr.relationship_description
  FROM contract_relationships cr
  JOIN contracts child ON cr.child_contract_id = child.id
  LEFT JOIN contracts parent ON cr.parent_contract_id = parent.id
  WHERE parent.reference_number ILIKE '%MSA%' OR cr.relationship_type ILIKE '%master%'

Find all children of a master agreement:
  SELECT c.contract_identifier, c.reference_number, c.title, cr.relationship_type
  FROM contract_relationships cr
  JOIN contracts c ON cr.child_contract_id = c.id
  WHERE cr.parent_contract_id = (SELECT id FROM contracts WHERE reference_number = 'MSA-ABC-202401-005')

Find contract family (parent + all children):
  WITH RECURSIVE contract_tree AS (
    -- Start with parent
    SELECT id, contract_identifier, reference_number, title, 0 as level
    FROM contracts WHERE reference_number = 'MSA-ABC-202401-005'
    UNION ALL
    -- Get children recursively
    SELECT c.id, c.contract_identifier, c.reference_number, c.title, ct.level + 1
    FROM contracts c
    JOIN contract_relationships cr ON c.id = cr.child_contract_id
    JOIN contract_tree ct ON cr.parent_contract_id = ct.id
  )
  SELECT * FROM contract_tree ORDER BY level, reference_number

Find orphaned relationships (parent not yet ingested):
  SELECT c.contract_identifier, cr.parent_reference_number, cr.relationship_type
  FROM contract_relationships cr
  JOIN contracts c ON cr.child_contract_id = c.id
  WHERE cr.parent_contract_id IS NULL

Find high-risk clauses:
  SELECT c.contract_identifier, cl.section_label, cl.text_content
  FROM clauses cl
  JOIN contracts c ON cl.contract_id = c.id
  WHERE cl.risk_level = 'high'

Semantic similarity (requires embedding vector):
  ORDER BY cl.embedding <=> '[vector]'::vector LIMIT 10

Graph: Party obligations:
  MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)-[:IMPOSES_OBLIGATION]->(o:Obligation)
  WHERE p.name =~ '.*party.*'
  RETURN p.name, c.title, o.description
"""

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
    
    except Exception as e:
        return f"SQL Query Error: {str(e)}\n\nQuery was: {sql_query}"


def get_database_schema() -> str:
    """Get the complete database schema, ontology, and query patterns.
    
    Use this first to understand the database structure before writing queries.
    Returns table schemas, column names, data types, relationships, and example query patterns.
    """
    return DATABASE_SCHEMA


def get_contract_family(
    reference_number: Annotated[str, Field(description="Reference number of the parent/master contract (e.g., 'MSA-ABC-202401-005')")],
    max_depth: Annotated[int, Field(description="Maximum depth to traverse (default 5)")] = 5
) -> str:
    """Get complete contract family tree showing parent contract and all descendants.
    
    This specialized tool finds:
    - The master/parent contract
    - All direct children (SOWs, amendments, addenda, work orders)
    - Nested relationships (e.g., amendments to SOWs under MSA)
    - Full hierarchy with levels
    
    Example: For a Master Services Agreement, returns:
    - Level 0: MSA-ABC-202401-005 (Master Services Agreement)
    - Level 1: SOW-ABC-202403-012 (Statement of Work)
    - Level 1: AMD-ABC-202406-025 (Amendment to MSA)
    - Level 2: WO-ABC-202404-015 (Work Order under SOW)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Recursive CTE to get contract tree
        query = """
        WITH RECURSIVE contract_tree AS (
            -- Start with the specified contract
            SELECT 
                c.id,
                c.contract_identifier,
                c.reference_number,
                c.title,
                c.contract_type,
                c.effective_date,
                c.status,
                0 as level,
                ARRAY[c.reference_number] as path,
                CAST(NULL AS TEXT) as relationship_type
            FROM contracts c
            WHERE c.reference_number = %s
            
            UNION ALL
            
            -- Get children recursively
            SELECT 
                c.id,
                c.contract_identifier,
                c.reference_number,
                c.title,
                c.contract_type,
                c.effective_date,
                c.status,
                ct.level + 1,
                ct.path || c.reference_number,
                cr.relationship_type
            FROM contracts c
            JOIN contract_relationships cr ON c.id = cr.child_contract_id
            JOIN contract_tree ct ON cr.parent_contract_id = ct.id
            WHERE ct.level < %s
        )
        SELECT 
            level,
            reference_number,
            title,
            contract_type,
            effective_date,
            status,
            relationship_type,
            array_to_string(path, ' -> ') as hierarchy_path
        FROM contract_tree
        ORDER BY level, reference_number
        """
        
        cur.execute(query, (reference_number, max_depth))
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return f"No contract found with reference number '{reference_number}'"
        
        # Format as hierarchical tree
        response = f"📋 **Contract Family Tree for {reference_number}**\n\n"
        
        for row in results:
            indent = "  " * row['level']
            level_icon = "📄" if row['level'] == 0 else "├─" if row['level'] == 1 else "│ ├─"
            
            response += f"{indent}{level_icon} **{row['reference_number']}**\n"
            response += f"{indent}   Title: {row['title']}\n"
            response += f"{indent}   Type: {row['contract_type']}\n"
            if row['relationship_type']:
                response += f"{indent}   Relationship: {row['relationship_type']}\n"
            response += f"{indent}   Status: {row['status']} | Date: {row['effective_date']}\n"
            response += f"{indent}   Path: {row['hierarchy_path']}\n\n"
        
        response += f"\n**Total contracts in family:** {len(results)}"
        response += f"\n**Maximum depth:** {max(r['level'] for r in results)}"
        
        return response
    
    except Exception as e:
        return f"Error getting contract family: {str(e)}"


# Legacy predefined functions removed - replaced by generic execute_sql_query and execute_cypher_query
# The agent now dynamically writes SQL and Cypher queries based on the database schema


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
            instructions="""You are a Contract Intelligence Assistant with direct access to a PostgreSQL database with Apache AGE graph capabilities.

**YOUR TOOLS:**

1. **get_database_schema** - Always call FIRST to understand tables, columns, and relationships
2. **execute_sql_query** - The main query tool that handles:
   • Standard SQL (JOINs, WHERE, GROUP BY, aggregations)
   • Semantic search via pgvector (ORDER BY embedding <=> %s)
   • Graph traversal via Apache AGE cypher() function
3. **get_contract_family** - Specialized tool for contract hierarchies:
   • Gets complete family tree for any master agreement
   • Shows all SOWs, amendments, addenda, work orders
   • Displays nested relationships with levels
   • Use when user asks about "contract family", "related contracts", "children", or "hierarchy"

**WORKFLOW:**

1. **Understand the schema**: Call get_database_schema() FIRST to see tables, columns, graph structure, and examples
2. **Plan your approach**: Determine what data you need and what query types to use
   - For contract families: Use contract_relationships table to find MSAs, SOWs, amendments
   - For obligations/rights: Use graph traversal with Apache AGE
   - For semantic content: Use vector similarity search
   - For analytics: Use standard SQL with aggregations
3. **Execute queries**: Use execute_sql_query with appropriate SQL/Cypher/semantic patterns
4. **For complex questions**: Make MULTIPLE tool calls to gather complete information
   - Example: First find master agreement, then get all related SOWs and amendments
   - Example: Analyze contract hierarchy, then drill into high-risk clauses in each document
   - Example: Get statistical overview, then examine specific relationships
   - Example: Combine SQL analytics with graph relationship analysis
5. **Synthesize results**: Combine insights from multiple queries into coherent answer

**QUERY PATTERNS:**

📊 **Standard SQL** (for analytics, filtering, aggregations):
```sql
SELECT c.contract_identifier, COUNT(cl.id) as clause_count
FROM contracts c
JOIN clauses cl ON c.id = cl.contract_id
WHERE c.contract_type = 'Service Agreement'
GROUP BY c.contract_identifier
LIMIT 20
```

🔗 **Contract Relationships** (for hierarchies, amendments, SOWs):
```sql
-- Find all SOWs under a Master Agreement
SELECT 
  parent.reference_number as master_agreement,
  child.reference_number as sow_reference,
  child.title as sow_title,
  cr.relationship_type
FROM contract_relationships cr
JOIN contracts child ON cr.child_contract_id = child.id
JOIN contracts parent ON cr.parent_contract_id = parent.id
WHERE parent.reference_number = 'MSA-ABC-202401-005'
  AND cr.relationship_type ILIKE '%statement of work%'
LIMIT 20
```

🌳 **Contract Family Tree** (recursive query for full hierarchy):
```sql
WITH RECURSIVE contract_tree AS (
  SELECT id, contract_identifier, reference_number, title, 0 as level,
         ARRAY[contract_identifier] as path
  FROM contracts WHERE reference_number = 'MSA-ABC-202401-005'
  UNION ALL
  SELECT c.id, c.contract_identifier, c.reference_number, c.title, ct.level + 1,
         ct.path || c.contract_identifier
  FROM contracts c
  JOIN contract_relationships cr ON c.id = cr.child_contract_id
  JOIN contract_tree ct ON cr.parent_contract_id = ct.id
  WHERE ct.level < 5  -- Prevent infinite loops
)
SELECT level, reference_number, title, path FROM contract_tree ORDER BY level, reference_number
LIMIT 50
```

🔍 **Semantic Search** (for finding similar content):
```sql
SELECT c.contract_identifier, cl.section_label, cl.text_content,
       1 - (cl.embedding <=> %s) as similarity
FROM clauses cl
JOIN contracts c ON cl.contract_id = c.id
ORDER BY cl.embedding <=> %s
LIMIT 20
```
Call with: need_embedding=True, search_text="liability and indemnification"

🕸️ **Graph Traversal** (for relationships and obligations):
```sql
SELECT * FROM cypher('contract_intelligence', $$
  MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)-[:IMPOSES_OBLIGATION]->(o:Obligation)
  WHERE p.name =~ '.*Acme.*'
  RETURN p.name, c.title, cl.section, o.description
  LIMIT 20
$$) as (party_name agtype, contract_title agtype, section agtype, obligation agtype)
```

**IMPORTANT GUIDELINES:**

✅ **DO:**
- Always include LIMIT (20-50 for initial queries)
- Use ILIKE '%term%' for case-insensitive text matching
- For semantic search: Use %s placeholder, set need_embedding=True
- For cypher(): Include column aliases with agtype for each return value
- Make multiple queries for complex questions - don't try to answer everything in one query
- Combine different query types (SQL + semantic + graph) when appropriate
- Use WHERE clauses to filter by risk_level, contract_type, dates

❌ **DON'T:**
- Try to compute embeddings yourself - use need_embedding=True
- Mix cypher() column aliases with SQL column types (always use agtype)
- Forget LIMIT clauses
- Try to answer complex multi-part questions with a single query

**MULTIPLE TOOL CALLS FOR COMPLEX QUESTIONS:**

When users ask complex questions like "analyze all contracts and their risks", break it down:
1. First query: Get list of contracts with basic stats
2. Second query: Analyze high-risk clauses separately
3. Third query: Use graph traversal to find obligation patterns
4. Synthesize: Combine all findings into comprehensive answer

This approach is MORE effective than trying to write one mega-query!

**OUTPUT FORMAT - BE CREATIVE WITH MARKDOWN:**

Your responses are rendered with a rich Markdown visualizer. Use these formatting features creatively:

📝 **Rich Text Formatting:**
- Use **bold** for emphasis, *italics* for subtle highlights
- Create clear section headers with ## and ###
- Use > blockquotes for important findings or legal implications
- Add horizontal rules (---) to separate major sections
- Use emojis strategically: ⚠️ (high risk), ⚡ (medium risk), ✓ (low risk), 📊 (statistics), 🔍 (findings), 💡 (insights)

📊 **Tables for Structured Data:**
```markdown
| Contract | Party | Risk Level | Key Findings |
|----------|-------|------------|--------------|
| contract_001 | Acme Corp | ⚠️ High | Unlimited liability |
| contract_002 | Beta Ltd | ✓ Low | Standard terms |
```

📈 **Mermaid Charts for Visualizations:**

Use Mermaid diagrams when they help communicate relationships, flows, or hierarchies:

**Contract Hierarchy Graphs:**
```mermaid
graph TD
    MSA[MSA-ABC-202401-005<br/>Master Services Agreement] --> SOW1[SOW-ABC-202403-012<br/>Development Services]
    MSA --> SOW2[SOW-ABC-202405-018<br/>Consulting Services]
    MSA --> AMD1[AMD-ABC-202406-025<br/>Rate Amendment]
    SOW1 --> WO1[WO-ABC-202404-015<br/>Work Order Q2]
    SOW1 --> WO2[WO-ABC-202407-029<br/>Work Order Q3]
    SOW2 --> ADD1[ADD-ABC-202406-022<br/>Addendum: Remote Work]
    
    style MSA fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    style SOW1 fill:#fff4e6,stroke:#ff9800
    style SOW2 fill:#fff4e6,stroke:#ff9800
    style AMD1 fill:#ffe6e6,stroke:#d32f2f
```

**Party-Contract Relationships:**
```mermaid
graph LR
    A[Acme Corp] -->|Vendor| B[Contract 001]
    A -->|Partner| C[Contract 008]
    B -->|Contains| D[High-Risk Clauses]
    C -->|Contains| E[Standard Terms]
```

**Process Flows:**
```mermaid
flowchart TD
    A[Contract Initiation] --> B{Type?}
    B -->|Service| C[Service Terms]
    B -->|Purchase| D[Purchase Terms]
    C --> E[Risk Assessment]
    D --> E
```

**Pie/Bar Charts for Statistics:**
```mermaid
pie title Contract Risk Distribution
    "High Risk" : 23
    "Medium Risk" : 45
    "Low Risk" : 32
```

**Timeline Visualizations:**
```mermaid
gantt
    title Contract Timeline
    section Acme Corp
    Contract 001 :2023-01-01, 365d
    Contract 008 :2023-06-01, 730d
```

**Example Rich Response:**

## 🔍 Analysis Results

Found **5 high-risk contracts** with liability concerns:

### ⚠️ Critical Findings

> **Unlimited Liability Exposure**: Contracts with Acme Corp lack caps on indemnification obligations.

| Contract ID | Party | Liability Cap | Risk Level |
|-------------|-------|---------------|------------|
| contract_001 | Acme Corp | Unlimited | ⚠️ High |
| contract_008 | Acme Corp | Unlimited | ⚠️ High |

```mermaid
graph TD
    A[Acme Corp] -->|Obligated to| B[Indemnify]
    B --> C[Unlimited Scope]
    B --> D[No Time Limit]
    C --> E[⚠️ HIGH RISK]
    D --> E
```

### 💡 Recommendations

1. **Immediate**: Negotiate liability caps for Acme Corp contracts
2. **Consider**: Standard $1M cap across all service agreements
3. **Review**: Similar unlimited obligations in other vendor contracts

**Key Principles:**
- Be visual when data has structure or relationships
- Use Mermaid for any flow, hierarchy, network, or distribution
- Make responses scannable with headers, tables, and formatting
- Cite specific contracts, sections, and parties
- Provide actionable insights

Remember: You dynamically write queries based on the schema. For complex questions, use multiple focused queries rather than one complicated query.""",
            tools=[
                get_database_schema,
                execute_sql_query,
                get_contract_family,
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
                if hasattr(content, 'text') and hasattr(content, 'type') and content.type == 'text':
                    reasoning += content.text
                
                # Check if this is a function call to execute_sql_query
                elif hasattr(content, 'name') and content.name == 'execute_sql_query':
                    # Parse the arguments to get the SQL query
                    if hasattr(content, 'parse_arguments'):
                        args = content.parse_arguments()
                        if args and 'sql_query' in args:
                            current_tool_calls.append({
                                'sql_query': args['sql_query'],
                                'reasoning': reasoning.strip() if reasoning else None,
                                'need_embedding': args.get('need_embedding', False),
                                'search_text': args.get('search_text', None),
                            })
            
            # Add tool calls from this message
            tool_calls.extend(current_tool_calls)
        
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
