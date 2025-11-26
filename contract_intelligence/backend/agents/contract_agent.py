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
   - contract_identifier (TEXT, UNIQUE) - e.g., 'contract_000_AcmeCorp'
   - title (TEXT)
   - contract_type (TEXT) - Values: 'Service Agreement', 'NDA', 'Purchase Order', 'Employment', etc.
   - effective_date (DATE)
   - expiration_date (DATE)
   - governing_law (TEXT)
   - file_path (TEXT)

2. clauses
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
        # Validate it's a SELECT query
        query_upper = sql_query.strip().upper()
        if not query_upper.startswith('SELECT'):
            return "Error: Only SELECT queries are allowed for security reasons."
        
        # Check for dangerous keywords
        dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
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

**YOUR TOOL:**

execute_sql_query - A single powerful tool that handles:
  • Standard SQL (JOINs, WHERE, GROUP BY, aggregations)
  • Semantic search via pgvector (ORDER BY embedding <=> %s)
  • Graph traversal via Apache AGE cypher() function

**WORKFLOW:**

1. **Understand the schema**: Call get_database_schema() FIRST to see tables, columns, graph structure, and examples
2. **Plan your approach**: Determine what data you need and what query types to use
3. **Execute queries**: Use execute_sql_query with appropriate SQL/Cypher/semantic patterns
4. **For complex questions**: Make MULTIPLE tool calls to gather complete information
   - Example: First get contract list, then analyze each one separately
   - Example: Get statistical overview, then drill into specific high-risk items
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

**OUTPUT FORMAT:**

- Cite specific contracts, sections, and parties
- Use emojis for risk levels: ⚠️ (high), ⚡ (medium), ✓ (low)
- Provide actionable insights and recommendations
- If no results, suggest query refinements

Remember: You dynamically write queries based on the schema. For complex questions, use multiple focused queries rather than one complicated query.""",
            tools=[
                get_database_schema,
                execute_sql_query,
            ],
        )
        self.thread = self.agent.get_new_thread()
    
    async def query_async(self, query_text: str) -> dict:
        """Execute a query asynchronously."""
        result = await self.agent.run(query_text, thread=self.thread)
        
        # Extract SQL queries from tool calls in the conversation
        sql_queries = []
        for message in result.messages:
            for content in message.contents:
                # Check if this is a function call to execute_sql_query
                if hasattr(content, 'name') and content.name == 'execute_sql_query':
                    # Parse the arguments to get the SQL query
                    if hasattr(content, 'parse_arguments'):
                        args = content.parse_arguments()
                        if args and 'sql_query' in args:
                            sql_queries.append(args['sql_query'])
        
        return {
            "query": query_text,
            "response": result.text,
            "source": "PostgreSQL with Apache AGE",
            "sql_queries": sql_queries,  # List of SQL queries executed
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
        "Show me statistics about our contract portfolio",
        "List all contracts involving Acme Corp and their details",
        "Find clauses about liability or indemnification using semantic search",
        "What are the high-risk clauses grouped by contract type?",
        "Use graph traversal to find all obligations for Acme Corp",
        "Show me rights granted to any party in the system",
        "Analyze the relationship network for contract_000"
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
