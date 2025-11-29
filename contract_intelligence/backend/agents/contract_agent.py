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


# def get_contract_family(
#     reference_number: Annotated[str, Field(description="Reference number of the parent/master contract (e.g., 'MSA-ABC-202401-005')")],
#     max_depth: Annotated[int, Field(description="Maximum depth to traverse (default 5)")] = 5
# ) -> str:
#     """Get complete contract family tree showing parent contract and all descendants.
    
#     This specialized tool finds:
#     - The master/parent contract
#     - All direct children (SOWs, amendments, addenda, work orders)
#     - Nested relationships (e.g., amendments to SOWs under MSA)
#     - Full hierarchy with levels
    
#     Example: For a Master Services Agreement, returns:
#     - Level 0: MSA-ABC-202401-005 (Master Services Agreement)
#     - Level 1: SOW-ABC-202403-012 (Statement of Work)
#     - Level 1: AMD-ABC-202406-025 (Amendment to MSA)
#     - Level 2: WO-ABC-202404-015 (Work Order under SOW)
#     """
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         # Recursive CTE to get contract tree
#         query = """
#         WITH RECURSIVE contract_tree AS (
#             -- Start with the specified contract
#             SELECT 
#                 c.id,
#                 c.contract_identifier,
#                 c.reference_number,
#                 c.title,
#                 c.contract_type,
#                 c.effective_date,
#                 c.status,
#                 0 as level,
#                 ARRAY[c.reference_number] as path,
#                 CAST(NULL AS TEXT) as relationship_type
#             FROM contracts c
#             WHERE c.reference_number = %s
            
#             UNION ALL
            
#             -- Get children recursively
#             SELECT 
#                 c.id,
#                 c.contract_identifier,
#                 c.reference_number,
#                 c.title,
#                 c.contract_type,
#                 c.effective_date,
#                 c.status,
#                 ct.level + 1,
#                 ct.path || c.reference_number,
#                 cr.relationship_type
#             FROM contracts c
#             JOIN contract_relationships cr ON c.id = cr.child_contract_id
#             JOIN contract_tree ct ON cr.parent_contract_id = ct.id
#             WHERE ct.level < %s
#         )
#         SELECT 
#             level,
#             reference_number,
#             title,
#             contract_type,
#             effective_date,
#             status,
#             relationship_type,
#             array_to_string(path, ' -> ') as hierarchy_path
#         FROM contract_tree
#         ORDER BY level, reference_number
#         """
        
#         cur.execute(query, (reference_number, max_depth))
#         results = cur.fetchall()
#         cur.close()
#         conn.close()
        
#         if not results:
#             return f"No contract found with reference number '{reference_number}'"
        
#         # Format as hierarchical tree
#         response = f"📋 **Contract Family Tree for {reference_number}**\n\n"
        
#         for row in results:
#             indent = "  " * row['level']
#             level_icon = "📄" if row['level'] == 0 else "├─" if row['level'] == 1 else "│ ├─"
            
#             response += f"{indent}{level_icon} **{row['reference_number']}**\n"
#             response += f"{indent}   Title: {row['title']}\n"
#             response += f"{indent}   Type: {row['contract_type']}\n"
#             if row['relationship_type']:
#                 response += f"{indent}   Relationship: {row['relationship_type']}\n"
#             response += f"{indent}   Status: {row['status']} | Date: {row['effective_date']}\n"
#             response += f"{indent}   Path: {row['hierarchy_path']}\n\n"
        
#         response += f"\n**Total contracts in family:** {len(results)}"
#         response += f"\n**Maximum depth:** {max(r['level'] for r in results)}"
        
#         return response
    
#     except Exception as e:
#         return f"Error getting contract family: {str(e)}"



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

## QUERY TOOLS

**execute_sql_query(sql_query, need_embedding=False, search_text=None)** - Main query tool for:
- Standard SQL (JOINs, WHERE, GROUP BY, aggregations)
- Contract hierarchies via contract_relationships table
- Semantic search: `ORDER BY embedding <=> %s` with need_embedding=True
- Graph traversal: `SELECT * FROM cypher('contract_intelligence', $$ ... $$) as (col1 agtype, ...)`


## QUERY PATTERNS

**Contract Relationships:**
```sql
-- Find SOWs under MSA
SELECT child.reference_number, child.title, cr.relationship_type
FROM contract_relationships cr
JOIN contracts child ON cr.child_contract_id = child.id
JOIN contracts parent ON cr.parent_contract_id = parent.id
WHERE parent.reference_number = 'MSA-ABC-202401-005'
LIMIT 20
```

**Recursive Family Tree:**
```sql
WITH RECURSIVE tree AS (
  SELECT id, reference_number, title, 0 as level
  FROM contracts WHERE reference_number = 'MSA-ABC-202401-005'
  UNION ALL
  SELECT c.id, c.reference_number, c.title, t.level + 1
  FROM contracts c
  JOIN contract_relationships cr ON c.id = cr.child_contract_id
  JOIN tree t ON cr.parent_contract_id = t.id
)
SELECT * FROM tree ORDER BY level LIMIT 50
```

**Semantic Search:**
```sql
SELECT c.contract_identifier, cl.text_content,
       1 - (cl.embedding <=> %s) as similarity
FROM clauses cl
JOIN contracts c ON cl.contract_id = c.id
ORDER BY cl.embedding <=> %s LIMIT 20
```
Use: need_embedding=True, search_text="liability limitations"

**Graph Traversal:**
```sql
SELECT * FROM cypher('contract_intelligence', $$
  MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)
  WHERE p.name =~ '.*Acme.*'
  RETURN p.name, c.title, cl.section
  LIMIT 20
$$) as (party agtype, contract agtype, section agtype)
```

## OUTPUT FORMATTING

Use Markdown with tables, emojis (⚠️ high, ⚡ medium, ✓ low), and Mermaid charts.

**Contract Hierarchy:**
```mermaid
graph TD
    MSA[MSA-ABC-001<br/>Master Agreement] --> SOW1[SOW-ABC-012<br/>Dev Services]
    MSA --> AMD1[AMD-ABC-025<br/>Amendment]
    style MSA fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    style SOW1 fill:#fff4e6,stroke:#ff9800
```

**Risk Distribution:**
```mermaid
pie title Risk Levels
    "High" : 23
    "Medium" : 45
    "Low" : 32
```

**Party Relationships:**
```mermaid
graph LR
    A[Acme Corp] -->|Vendor| B[Contract 001]
    A -->|Partner| C[Contract 008]
```

## GUIDELINES

✅ Always use LIMIT (20-50), ILIKE for case-insensitive search
✅ For complex questions, make multiple focused queries
✅ Combine SQL + semantic + graph when appropriate
❌ No INSERT/UPDATE/DELETE - read-only queries only
❌ Don't compute embeddings yourself - use need_embedding=True""",
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
