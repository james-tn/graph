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
    sql_query: Annotated[str, Field(description="SQL query to execute. Must be a valid PostgreSQL SELECT statement. Use proper JOINs and WHERE clauses based on the schema.")],
    need_embedding: Annotated[bool, Field(description="Set to True if query needs semantic search with embedding vector")] = False,
    search_text: Annotated[str | None, Field(description="Text to generate embedding for (only if need_embedding=True)")] = None
) -> str:
    """Execute a SQL query against the PostgreSQL database.
    
    Use this to:
    - Query contracts, clauses, parties, and relationships
    - Perform aggregations and analytics
    - Filter by dates, risk levels, contract types
    - Search using ILIKE patterns
    - Execute semantic similarity searches (when need_embedding=True)
    
    IMPORTANT:
    - Only SELECT queries are allowed (no INSERT/UPDATE/DELETE)
    - Use LIMIT to restrict results (recommended: 20-50)
    - For semantic search, set need_embedding=True and provide search_text
    - The embedding vector will be automatically inserted as %s placeholder
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


def execute_cypher_query(
    cypher_pattern: Annotated[str, Field(description="Cypher MATCH pattern and RETURN clause. Do not include the cypher() function wrapper - just the Cypher query itself.")],
    return_columns: Annotated[str, Field(description="Comma-separated list of column names and types for the RETURN clause, e.g. 'party agtype, contract agtype, count agtype'")] 
) -> str:
    """Execute an Apache AGE Cypher graph query for multi-hop relationship traversal.
    
    Use this to:
    - Find obligations for parties (Party -> Contract -> Clause -> Obligation)
    - Find rights granted to parties (Party -> Right <- Clause <- Contract)
    - Analyze complete relationship networks
    - Perform multi-hop graph traversals
    
    Example cypher_pattern:
        MATCH (p:Party)-[:IS_PARTY_TO]->(c:Contract)-[:CONTAINS_CLAUSE]->(cl:Clause)-[:IMPOSES_OBLIGATION]->(o:Obligation)
        WHERE p.name =~ '.*Acme.*'
        RETURN p.name as party, c.title as contract, o.description as obligation
        LIMIT 20
    
    Example return_columns:
        party agtype, contract agtype, obligation agtype
    
    IMPORTANT:
    - Use =~ for regex matching (case-insensitive: '.*term.*')
    - Always include LIMIT (max 50)
    - Node labels: Contract, Clause, Party, Obligation, Right
    - Relationships: IS_PARTY_TO, CONTAINS_CLAUSE, IMPOSES_OBLIGATION, GRANTS_RIGHT, HOLDS_RIGHT
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Set search path for AGE
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Construct full query
        full_query = f"""
        SELECT * FROM ag_catalog.cypher('{GRAPH_NAME}', $$
            {cypher_pattern}
        $$) as ({return_columns});
        """
        
        cur.execute(full_query)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return "Graph query executed successfully but returned no results."
        
        # Format results
        columns = results[0].keys()
        response = f"Found {len(results)} result(s) via graph traversal:\n\n"
        
        for i, row in enumerate(results, 1):
            response += f"{i}. "
            for col in columns:
                value = str(row[col])
                # Clean up agtype formatting
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                response += f"{col}: {value}, "
            response = response.rstrip(', ') + "\n"
        
        return response
    
    except Exception as e:
        return f"Cypher Query Error: {str(e)}\n\nPattern was: {cypher_pattern}\n\nReturn columns: {return_columns}"


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
            instructions="""You are a Contract Intelligence Assistant with direct access to a PostgreSQL database.

You have TWO powerful capabilities:

1. **SQL Query Execution** (use execute_sql_query tool)
   - Write SELECT queries based on the database schema
   - Join tables, filter data, perform aggregations
   - Use ILIKE for case-insensitive pattern matching
   - Execute semantic similarity searches with embeddings
   - Use full-text search with @@ and ts_rank

2. **Graph Traversal** (use execute_cypher_query tool)
   - Write Cypher MATCH patterns for multi-hop relationships
   - Traverse Party -> Contract -> Clause -> Obligation/Right paths
   - Use graph queries for complex relationship analysis

**WORKFLOW:**

1. **First**: Call get_database_schema() to see tables, columns, relationships, and query patterns
2. **Then**: Write appropriate SQL or Cypher queries based on the user's question
3. **Execute**: Use execute_sql_query for data queries, execute_cypher_query for relationship traversal
4. **Analyze**: Interpret results and provide insights to the user

**QUERY WRITING GUIDELINES:**

- **Always LIMIT results** (20-50 for display, more if needed for analysis)
- **Use proper JOINs** when querying across tables
- **Filter by risk_level** when user asks about risks ('high', 'medium', 'low')
- **Use ILIKE '%term%'** for flexible name/text matching
- **For semantic search**: Set need_embedding=True and provide search_text
- **For graph queries**: Use =~ for regex patterns like '.*company.*'
- **Include relevant columns** in SELECT to provide complete answers

**WHEN TO USE EACH TOOL:**

- **SQL**: Statistics, listings, filtering, searching, analytics
  Example: "Show contracts by type", "Find clauses about liability", "List high-risk items"
  
- **Cypher/Graph**: Relationships, obligations, rights, multi-hop connections
  Example: "What obligations does Party X have?", "Find rights granted to Party Y", "Analyze contract relationships"

**OUTPUT FORMAT:**

- Cite specific contracts, sections, and parties
- Highlight risk levels with emojis: ⚠️ (high), ⚡ (medium), ✓ (low)
- Provide context and actionable insights
- If query returns no results, explain why and suggest alternatives

Remember: You are writing queries dynamically based on the schema, not using predefined queries.""",
            tools=[
                get_database_schema,
                execute_sql_query,
                execute_cypher_query,
            ],
        )
        self.thread = self.agent.get_new_thread()
    
    async def query_async(self, query_text: str) -> dict:
        """Execute a query asynchronously."""
        result = await self.agent.run(query_text, thread=self.thread)
        return {
            "query": query_text,
            "response": result.text,
            "source": "PostgreSQL with Apache AGE",
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
