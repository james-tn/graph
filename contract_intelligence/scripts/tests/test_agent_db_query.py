#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Test script demonstrating AI agent translating natural language questions
into PostgreSQL graph and vector database queries.

This example uses the Agent Framework to create an agent that can:
1. Understand natural language questions about data
2. Translate them into SQL/Cypher queries
3. Execute queries against PostgreSQL with pgvector and Apache AGE extensions
4. Return results in natural language
"""

import asyncio
import os
from typing import Annotated, Any

import numpy as np
import psycopg2
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from openai import OpenAI
from pydantic import Field

# Database connection parameters
DB_HOST = "ci-ci-dev-pgflex.postgres.database.azure.com"
DB_NAME = "cipgraph"
DB_USER = "pgadmin"
DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")

if not DB_PASSWORD:
    print("ERROR: POSTGRES_ADMIN_PASSWORD environment variable not set")
    exit(1)

# OpenAI client for embeddings
openai_client = OpenAI(
    api_key=os.environ.get("GRAPHRAG_API_KEY"),
    base_url=os.environ.get("GRAPHRAG_API_BASE") + "/openai/v1/"
)


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for text using Azure OpenAI."""
    response = openai_client.embeddings.create(
        input=text,
        model=os.environ.get("GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME")
    )
    return response.data[0].embedding


def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )


def search_similar_documents(
    query_text: Annotated[str, Field(description="The text query to search for similar documents")],
    top_k: Annotated[int, Field(description="Number of top results to return")] = 3
) -> str:
    """
    Search for documents similar to the query text using vector similarity.
    Returns the most similar documents based on semantic similarity.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Generate embedding for the query using Azure OpenAI
        query_embedding = get_embedding(query_text)
        
        # Search for similar documents using cosine similarity
        cur.execute("""
            SELECT title, content, 
                   1 - (embedding <=> %s::vector) as similarity
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, top_k))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return "No similar documents found."
        
        response = f"Found {len(results)} similar documents:\n\n"
        for i, (title, content, similarity) in enumerate(results, 1):
            response += f"{i}. {title} (similarity: {similarity:.4f})\n"
            response += f"   Content: {content}\n\n"
        
        return response
    
    except Exception as e:
        return f"Error searching documents: {str(e)}"


def query_graph_relationships(
    person_name: Annotated[str, Field(description="The name of the person to query relationships for")]
) -> str:
    """
    Query the organizational graph to find relationships for a specific person.
    Returns information about who they report to and who they collaborate with.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Set search path for AGE
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Query relationships for the person
        cur.execute("""
            SELECT * FROM cypher('test_graph', $$
                MATCH (p:Person {name: '%s'})-[r]->(other:Person)
                RETURN type(r) as relationship, other.name as other_person, other.role as role
            $$) as (relationship agtype, other_person agtype, role agtype);
        """ % person_name)
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return f"No relationships found for {person_name}. They may not exist in the graph."
        
        response = f"Relationships for {person_name}:\n\n"
        for relationship, other_person, role in results:
            # Parse AGE type results (they come as strings)
            rel_type = str(relationship).strip('"')
            other_name = str(other_person).strip('"')
            other_role = str(role).strip('"')
            response += f"- {rel_type}: {other_name} ({other_role})\n"
        
        return response
    
    except Exception as e:
        return f"Error querying graph: {str(e)}"


def find_team_members(
    manager_name: Annotated[str, Field(description="The name of the manager to find team members for")]
) -> str:
    """
    Find all people who report to a specific manager in the organizational graph.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Set search path for AGE
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Find all people who report to the manager
        cur.execute("""
            SELECT * FROM cypher('test_graph', $$
                MATCH (p:Person)-[r:REPORTS_TO]->(m:Person {name: '%s'})
                RETURN p.name as employee_name, p.role as employee_role
            $$) as (employee_name agtype, employee_role agtype);
        """ % manager_name)
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return f"No team members found reporting to {manager_name}."
        
        response = f"Team members reporting to {manager_name}:\n\n"
        for i, (employee_name, employee_role) in enumerate(results, 1):
            name = str(employee_name).strip('"')
            role = str(employee_role).strip('"')
            response += f"{i}. {name} - {role}\n"
        
        return response
    
    except Exception as e:
        return f"Error finding team members: {str(e)}"


def find_collaborators(
    person_name: Annotated[str, Field(description="The name of the person to find collaborators for")]
) -> str:
    """
    Find all people who collaborate with a specific person in the organizational graph.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Set search path for AGE
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Find all collaborators (bidirectional relationship)
        cur.execute("""
            SELECT * FROM cypher('test_graph', $$
                MATCH (p:Person {name: '%s'})-[r:COLLABORATES_WITH]-(other:Person)
                RETURN other.name as collaborator_name, other.role as collaborator_role
            $$) as (collaborator_name agtype, collaborator_role agtype);
        """ % person_name)
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return f"No collaborators found for {person_name}."
        
        response = f"Collaborators of {person_name}:\n\n"
        for i, (collaborator_name, collaborator_role) in enumerate(results, 1):
            name = str(collaborator_name).strip('"')
            role = str(collaborator_role).strip('"')
            response += f"{i}. {name} - {role}\n"
        
        return response
    
    except Exception as e:
        return f"Error finding collaborators: {str(e)}"


def list_all_people() -> str:
    """
    List all people in the organizational graph database.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Set search path for AGE
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Get all people from the graph
        cur.execute("""
            SELECT * FROM cypher('test_graph', $$
                MATCH (p:Person)
                RETURN p.name as name, p.role as role
            $$) as (name agtype, role agtype);
        """)
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return "No people found in the graph."
        
        response = f"People in the organization ({len(results)} total):\n\n"
        for i, (name, role) in enumerate(results, 1):
            person_name = str(name).strip('"')
            person_role = str(role).strip('"')
            response += f"{i}. {person_name} - {person_role}\n"
        
        return response
    
    except Exception as e:
        return f"Error listing people: {str(e)}"


async def main() -> None:
    """Main function demonstrating AI agent querying graph and vector database."""
    
    print("=" * 70)
    print("AI Agent + PostgreSQL Graph & Vector Database Demo")
    print("=" * 70)
    print()
    
    # Initialize database with test data if needed
    print("Setting up test data...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Set search path for AGE
        cur.execute("SET search_path = ag_catalog, '$user', public;")
        
        # Check if test_graph exists
        cur.execute("SELECT * FROM ag_catalog.ag_graph WHERE name = 'test_graph';")
        if not cur.fetchone():
            print("Creating test graph and data...")
            
            # Create the graph
            cur.execute("SELECT create_graph('test_graph');")
            conn.commit()
            
            # Create nodes (people)
            people = [
                ("Alice", "Engineer"),
                ("Bob", "Manager"),
                ("Carol", "Designer"),
                ("Dave", "Engineer")
            ]
            
            for name, role in people:
                cur.execute("""
                    SELECT * FROM cypher('test_graph', $$
                        CREATE (p:Person {name: '%s', role: '%s'})
                        RETURN p
                    $$) as (p agtype);
                """ % (name, role))
                conn.commit()
            
            # Create relationships
            relationships = [
                ("Alice", "Bob", "REPORTS_TO"),
                ("Dave", "Bob", "REPORTS_TO"),
                ("Carol", "Bob", "REPORTS_TO"),
                ("Alice", "Dave", "COLLABORATES_WITH"),
                ("Alice", "Carol", "COLLABORATES_WITH")
            ]
            
            for from_name, to_name, rel_type in relationships:
                cur.execute("""
                    SELECT * FROM cypher('test_graph', $$
                        MATCH (a:Person {name: '%s'}), (b:Person {name: '%s'})
                        CREATE (a)-[:%s]->(b)
                    $$) as (result agtype);
                """ % (from_name, to_name, rel_type))
                conn.commit()
            
            print("✓ Test graph created")
        else:
            print("✓ Test graph already exists")
        
        # Reset search path to public for documents table
        cur.execute("SET search_path = public;")
        
        # Check if documents table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'documents'
            );
        """)
        if not cur.fetchone()[0]:
            print("Creating documents table with vector data...")
            
            # Create documents table
            cur.execute("""
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    embedding vector(1536)
                );
            """)
            
            # Insert sample documents
            documents = [
                ("Tutorial on vector databases", "Learn about vector databases and semantic search..."),
                ("Guide to graph algorithms", "Explore graph algorithms like BFS, DFS, and shortest path..."),
                ("Article on database optimization", "Tips and tricks for optimizing database performance..."),
                ("Document about AI and machine learning", "Introduction to AI, ML, and deep learning concepts..."),
                ("Technical guide to Python programming", "Master Python programming for data science...")
            ]
            
            for title, content in documents:
                # Generate real embedding using Azure OpenAI
                embedding = get_embedding(content)
                cur.execute("""
                    INSERT INTO documents (title, content, embedding)
                    VALUES (%s, %s, %s)
                """, (title, content, embedding))
            
            # Create HNSW index
            cur.execute("""
                CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
            """)
            
            conn.commit()
            print("✓ Documents table created")
        else:
            print("✓ Documents table already exists")
        
        cur.close()
        conn.close()
        print()
        
    except Exception as e:
        print(f"Error setting up test data: {e}")
        print()
    
    # Create agent with database query tools
    # For authentication, run `az login` command in terminal
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="""You are a helpful assistant that can query a PostgreSQL database 
        with vector and graph capabilities. You have access to:
        
        1. Vector search: Find semantically similar documents
        2. Graph queries: Navigate organizational relationships (REPORTS_TO, COLLABORATES_WITH)
        
        When users ask questions, determine which tool(s) to use and provide clear, 
        natural language responses based on the query results.""",
        tools=[
            search_similar_documents,
            query_graph_relationships,
            find_team_members,
            find_collaborators,
            list_all_people
        ],
    )
    
    # Create a thread for maintaining conversation context
    thread = agent.get_new_thread()
    
    # Example queries demonstrating natural language to database queries
    queries = [
        "Who are all the people in the organization?",
        "Who does Alice report to and who does she collaborate with?",
        "Show me Bob's team members",
        "Who collaborates with Carol?",
        "Find me documents similar to 'machine learning optimization'"
    ]
    
    for query in queries:
        print(f"\n{'─' * 70}")
        print(f"User: {query}")
        print(f"{'─' * 70}")
        
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
