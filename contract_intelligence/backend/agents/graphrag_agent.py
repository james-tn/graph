#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Microsoft GraphRAG Agent for Contract Intelligence — v3

Provides knowledge graph-based search capabilities using GraphRAG v3:
- Local Search: Entity-centric queries with community context
- Global Search: High-level summaries across entire corpus
- DRIFT Search: Entity-focused + community context (new in v2+)
- Basic Search: Standard top-k vector search (new in v3)
- Community Detection: Thematic groupings of related information

Key v3 changes:
- Uses graphrag.api for search (preferred over internal wiring)
- LiteLLM replaces fnllm as model manager
- Custom PgVectorStore shares PostgreSQL with contract_agent
- Monorepo sub-packages (graphrag-vectors, graphrag-storage, etc.)
"""

import asyncio
import os
from pathlib import Path
from typing import Literal

import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GraphRAGAgent:
    """Agent for querying Microsoft GraphRAG v3 knowledge graph.
    
    Supports both LanceDB (default CLI) and PgVector (shared PostgreSQL)
    as the vector store backend.
    """
    
    def __init__(
        self,
        root_dir: Path = Path("."),
        use_pgvector: bool = True,
    ):
        """Initialize GraphRAG agent with configuration.
        
        Args:
            root_dir: Project root directory containing graphrag_config/ and data/
            use_pgvector: If True, use PostgreSQL pgvector (shared instance).
                         If False, use LanceDB (default GraphRAG behavior).
        """
        self.root_dir = root_dir
        self.use_pgvector = use_pgvector
        
        # Environment configuration
        self.api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        # Validate required environment variables
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        if not self.api_base:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.llm_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        self.embedding_deployment = os.environ.get("EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small")
        
        # Paths to GraphRAG output
        self.output_dir = root_dir / "data" / "output"
        self.lancedb_dir = self.output_dir / "lancedb"
        
        # Lazy-loaded data
        self._entities_df = None
        self._relationships_df = None
        self._communities_df = None
        self._community_reports_df = None
        self._text_units_df = None
        self._covariates_df = None
        
        # Search engines (lazy init)
        self._local_search_engine = None
        self._global_search_engine = None
        self._description_embedding_store = None
        
        # Register pgvector if requested
        if self.use_pgvector:
            self._register_pgvector()
    
    def _register_pgvector(self):
        """Register PgVectorStore with GraphRAG's factory."""
        try:
            from graphrag_vectors import register_vector_store
            from backend.vector_stores.pgvector_store import PgVectorStore
            
            register_vector_store("pgvector", PgVectorStore)
            print("✓ Registered PgVectorStore with GraphRAG factory")
        except ImportError as e:
            print(f"⚠️ Could not register PgVectorStore: {e}")
            print("  Falling back to LanceDB")
            self.use_pgvector = False
    
    def _load_parquet_data(self):
        """Load GraphRAG indexed data from parquet files."""
        if self._entities_df is not None:
            return  # Already loaded
        
        print("📚 Loading GraphRAG v3 data from parquet...")
        
        if not self.output_dir.exists():
            raise FileNotFoundError(
                f"GraphRAG output not found at {self.output_dir}. "
                "Run GraphRAG indexing first."
            )
        
        # Load all parquet tables
        tables = {
            "entities": "entities.parquet",
            "relationships": "relationships.parquet",
            "communities": "communities.parquet",
            "community_reports": "community_reports.parquet",
            "text_units": "text_units.parquet",
            "covariates": "covariates.parquet",
        }
        
        for attr, filename in tables.items():
            path = self.output_dir / filename
            if path.exists():
                df = pd.read_parquet(path)
                setattr(self, f"_{attr}_df", df)
                print(f"  ✓ Loaded {len(df)} {attr}")
            else:
                setattr(self, f"_{attr}_df", pd.DataFrame())
                optional = "(optional)" if attr == "covariates" else ""
                print(f"  {'ℹ️' if optional else '⚠️'} {attr} not found {optional}")
    
    def _get_description_embedding_store(self):
        """Get the vector store for entity description embeddings."""
        if self._description_embedding_store is not None:
            return self._description_embedding_store
        
        if self.use_pgvector:
            from backend.vector_stores.pgvector_store import PgVectorStore
            
            store = PgVectorStore(
                index_name="entity_description",
                vector_size=1536,
            )
            store.connect()
            self._description_embedding_store = store
            print("  ✓ Connected to pgvector entity embedding store")
        else:
            # Fall back to LanceDB
            from graphrag_vectors.lancedb import LanceDBVectorStore
            
            store = LanceDBVectorStore(
                index_name="entity_description",
                vector_size=1536,
                db_uri=str(self.lancedb_dir),
            )
            store.connect()
            self._description_embedding_store = store
            print("  ✓ Connected to LanceDB entity embedding store")
        
        return self._description_embedding_store
    
    def _setup_local_search(self):
        """Setup local search engine using GraphRAG v3 API."""
        if self._local_search_engine is not None:
            return
        
        self._load_parquet_data()
        
        if self._entities_df.empty:
            print("  ⚠️ No entities loaded, local search unavailable")
            self._local_search_engine = "not_available"
            return
        
        print("  Setting up local search engine (v3)...")
        
        try:
            from graphrag.config.load_config import load_config
            from graphrag.query.factory import get_local_search_engine
            from graphrag.query.indexer_adapters import (
                read_indexer_covariates,
                read_indexer_entities,
                read_indexer_relationships,
                read_indexer_reports,
                read_indexer_text_units,
            )
            
            # Load GraphRAG config
            config_dir = self.root_dir / "graphrag_config"
            config = load_config(config_dir)
            
            # Determine community level
            community_level = (
                int(self._communities_df["level"].max())
                if not self._communities_df.empty
                else 0
            )
            print(f"  ℹ️ Community level: {community_level}")
            
            # Parse data using indexer adapters
            entities = read_indexer_entities(
                self._entities_df, self._communities_df, community_level
            )
            relationships = read_indexer_relationships(self._relationships_df)
            reports = read_indexer_reports(
                self._community_reports_df, self._communities_df, community_level
            )
            text_units = read_indexer_text_units(self._text_units_df)
            covariates = (
                read_indexer_covariates(self._covariates_df)
                if not self._covariates_df.empty
                else []
            )
            
            # Get vector store
            description_store = self._get_description_embedding_store()
            
            # Create local search engine
            self._local_search_engine = get_local_search_engine(
                config=config,
                reports=reports,
                text_units=text_units,
                entities=entities,
                relationships=relationships,
                covariates={"claims": covariates},
                response_type="concise with visualizations",
                description_embedding_store=description_store,
            )
            
            print("  ✓ Local search engine ready")
            
        except Exception as e:
            print(f"  ⚠️ Local search setup failed: {e}")
            import traceback
            traceback.print_exc()
            self._local_search_engine = "not_available"
    
    def _setup_global_search(self):
        """Setup global search engine — simplified community report search."""
        if self._global_search_engine is not None:
            return
        
        self._load_parquet_data()
        print("  ℹ️ Using simplified global search (community reports)")
        self._global_search_engine = "simplified"
    
    async def local_search(self, query: str) -> dict:
        """Execute local search for entity-specific queries.
        
        Best for: specific contracts, party obligations, detailed relationships.
        """
        self._setup_local_search()
        
        if self._local_search_engine == "not_available":
            print("  → Falling back to global search")
            return await self.global_search(query)
        
        try:
            result = await self._local_search_engine.search(query)
            
            context_data = getattr(result, "context_data", {})
            if context_data:
                serializable = {}
                for key, value in context_data.items():
                    if hasattr(value, "to_dict"):
                        serializable[key] = value.to_dict("records")
                    else:
                        serializable[key] = value
                context_data = serializable
            
            return {
                "query": query,
                "search_type": "local",
                "response": result.response,
                "context_data": context_data,
                "context_text": getattr(result, "context_text", ""),
                "completion_time": getattr(result, "completion_time", 0),
                "llm_calls": getattr(result, "llm_calls", 0),
            }
        except Exception as e:
            print(f"  Local search failed: {e}")
            import traceback
            traceback.print_exc()
            return await self.global_search(query)
    
    async def global_search(self, query: str) -> dict:
        """Execute global search for high-level queries.
        
        Best for: cross-contract patterns, trends, risk summaries.
        """
        self._setup_global_search()
        
        if self._global_search_engine == "simplified":
            return await self._simplified_global_search(query)
        
        result = await self._global_search_engine.asearch(query)
        
        context_data = getattr(result, "context_data", {})
        if context_data:
            serializable = {}
            for key, value in context_data.items():
                if hasattr(value, "to_dict"):
                    serializable[key] = value.to_dict("records")
                else:
                    serializable[key] = value
            context_data = serializable
        
        return {
            "query": query,
            "search_type": "global",
            "response": result.response,
            "context_data": context_data,
            "context_text": getattr(result, "context_text", ""),
            "completion_time": getattr(result, "completion_time", 0),
            "llm_calls": getattr(result, "llm_calls", 0),
            "map_responses": getattr(result, "map_responses", []),
        }
    
    async def _simplified_global_search(self, query: str) -> dict:
        """Global search using community reports + LLM summarization."""
        if self._community_reports_df is None or self._community_reports_df.empty:
            return {
                "query": query,
                "search_type": "global",
                "response": "No community reports available. Run GraphRAG indexing first.",
                "context_data": {},
                "context_text": "",
                "completion_time": 0,
                "llm_calls": 0,
            }
        
        relevant_reports = []
        for _, row in self._community_reports_df.iterrows():
            content = row.get("full_content") or row.get("summary") or row.get("title", "")
            if content:
                relevant_reports.append(str(content)[:3000])
            if len(relevant_reports) >= 10:
                break
        
        if not relevant_reports:
            return {
                "query": query,
                "search_type": "global",
                "response": "No report content available.",
                "context_data": {},
                "context_text": "",
                "completion_time": 0,
                "llm_calls": 0,
            }
        
        context = "\n\n---\n\n".join(relevant_reports)
        
        prompt = f"""Based on the following contract analysis reports, answer this question concisely with rich visualizations.

Question: {query}

Reports:
{context}

**CRITICAL: Be BRIEF (2-3 sentences max), then show Mermaid charts.**
Use emojis: 📊 🔍 💡 ⚠️ ✓ ❌ 🎯
Bold key numbers. Use pie/graph/xychart-beta/gantt charts.
ALWAYS quote labels with special chars in Mermaid: ["Label (with parens)"]"""
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.llm_deployment,
                max_completion_tokens=8000,
            )
            answer = response.choices[0].message.content or "No response generated."
            
            return {
                "query": query,
                "search_type": "global",
                "response": answer,
                "context_data": {"num_reports": len(relevant_reports)},
                "context_text": context[:1000] + "...",
                "completion_time": 0,
                "llm_calls": 1,
                "map_responses": [],
            }
        except Exception as e:
            return {
                "query": query,
                "search_type": "global",
                "response": f"Error: {e}",
                "context_data": {"error": str(e)},
                "context_text": "",
                "completion_time": 0,
                "llm_calls": 0,
                "map_responses": [],
            }
    
    async def hybrid_search(
        self,
        query: str,
        search_type: Literal["auto", "local", "global"] = "auto",
    ) -> dict:
        """Execute hybrid search with automatic routing."""
        if search_type == "auto":
            global_keywords = [
                "all contracts", "across contracts", "overall", "trend", "pattern",
                "compare", "comparison", "summary", "overview", "industry",
                "common", "typical", "generally", "most", "least",
            ]
            query_lower = query.lower()
            search_type = (
                "global"
                if any(kw in query_lower for kw in global_keywords)
                else "local"
            )
        
        if search_type == "global":
            return await self.global_search(query)
        return await self.local_search(query)
    
    def query(
        self,
        query_text: str,
        search_type: Literal["auto", "local", "global"] = "auto",
    ) -> dict:
        """Synchronous wrapper for hybrid search."""
        return asyncio.run(self.hybrid_search(query_text, search_type))


# Convenience functions
def query_graphrag(
    query: str,
    search_type: Literal["auto", "local", "global"] = "auto",
    use_pgvector: bool = True,
) -> dict:
    """Query GraphRAG knowledge graph."""
    agent = GraphRAGAgent(use_pgvector=use_pgvector)
    return agent.query(query, search_type)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python graphrag_agent.py '<query>' [local|global|auto] [--lancedb]")
        sys.exit(1)
    
    query_text = sys.argv[1]
    search_type_arg = sys.argv[2] if len(sys.argv) > 2 else "auto"
    use_pg = "--lancedb" not in sys.argv
    
    print(f"🔍 GraphRAG Query: {query_text}")
    print(f"   Search Type: {search_type_arg}")
    print(f"   Vector Store: {'pgvector' if use_pg else 'LanceDB'}\n")
    
    result = query_graphrag(query_text, search_type_arg, use_pgvector=use_pg)
    
    print("\n" + "=" * 70)
    print(f"Search Type: {result['search_type'].upper()}")
    print("=" * 70)
    print(result["response"])
    print("\n" + "=" * 70)
    print(f"⏱️ Completed in {result.get('completion_time', 0):.2f}s")
    print(f"🤖 LLM Calls: {result.get('llm_calls', 0)}")
