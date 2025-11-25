#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Microsoft GraphRAG Agent for Contract Intelligence

Provides knowledge graph-based search capabilities:
- Local Search: Entity-centric queries with community context
- Global Search: High-level summaries across entire corpus
- Community Detection: Thematic groupings of related information
"""

import asyncio
import os
from pathlib import Path
from typing import Literal

import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.config.models.vector_store_schema_config import VectorStoreSchemaConfig
from graphrag.language_model.manager import ModelManager
from graphrag.language_model.providers.fnllm.utils import get_openai_model_parameters_from_config
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.structured_search.global_search.community_context import (
    GlobalCommunityContext,
)
from graphrag.query.structured_search.global_search.search import GlobalSearch
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.tokenizer.get_tokenizer import get_tokenizer
from graphrag.vector_stores.lancedb import LanceDBVectorStore


class GraphRAGAgent:
    """Agent for querying Microsoft GraphRAG knowledge graph."""
    
    def __init__(self, root_dir: Path = Path(".")):
        """Initialize GraphRAG agent with configuration."""
        self.root_dir = root_dir
        
        # Environment configuration
        self.api_key = os.environ.get("GRAPHRAG_API_KEY")
        self.api_base = os.environ.get("GRAPHRAG_API_BASE")
        
        # Validate required environment variables
        if not self.api_key:
            raise ValueError("GRAPHRAG_API_KEY environment variable is required")
        if not self.api_base:
            raise ValueError("GRAPHRAG_API_BASE environment variable is required")
        
        self.api_version = os.environ.get("GRAPHRAG_API_VERSION", "2024-02-15-preview")
        self.llm_deployment = os.environ.get("GRAPHRAG_LLM_DEPLOYMENT_NAME", "gpt-4o")
        self.embedding_deployment = os.environ.get("GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small")
        
        # Paths to GraphRAG output (matches GraphRAG config: data/output)
        self.output_dir = root_dir / "data" / "output"
        self.artifacts_dir = self.output_dir / "artifacts"
        self.lancedb_dir = self.output_dir / "lancedb"
        
        # Initialize models using LiteLLM through ModelManager
        from graphrag.config.models.language_model_config import LanguageModelConfig
        
        # Create chat model config
        chat_config = LanguageModelConfig(
            type="azure_openai_chat",
            model=self.llm_deployment,
            api_key=self.api_key,
            api_base=self.api_base,
            api_version=self.api_version,
            deployment_name=self.llm_deployment,
            encoding_model="cl100k_base",  # Standard encoding for GPT-4 models
        )
        
        # Create embedding model config
        embedding_config = LanguageModelConfig(
            type="azure_openai_embedding",
            model=self.embedding_deployment,
            api_key=self.api_key,
            api_base=self.api_base,
            api_version=self.api_version,
            deployment_name=self.embedding_deployment,
            encoding_model="cl100k_base",  # Standard encoding for embeddings
        )
        
        # Initialize models
        self.llm = ModelManager().get_or_create_chat_model(
            name="graphrag_chat",
            model_type=chat_config.type,
            config=chat_config,
        )
        
        self.embedding_model = ModelManager().get_or_create_embedding_model(
            name="graphrag_embedding",
            model_type=embedding_config.type,
            config=embedding_config,
        )
        
        self.tokenizer = get_tokenizer(model_config=chat_config)
        self.model_params = get_openai_model_parameters_from_config(chat_config)
        
        # Load data lazily
        self._entities = None
        self._communities = None
        self._relationships = None
        self._reports = None
        self._text_units = None
        self._covariates = None
        self._description_embedding_store = None
        
        self._local_search_engine = None
        self._global_search_engine = None
    
    def _load_data(self):
        """Load GraphRAG indexed data from LanceDB (GraphRAG 2.x format)."""
        if self._entities is not None:
            return  # Already loaded
        
        print("📚 Loading GraphRAG data from LanceDB...")
        
        # GraphRAG 2.x stores data in LanceDB with JSON attributes
        # We need to parse the attributes column to get the full data structure
        import lancedb
        import json
        
        db = lancedb.connect(str(self.lancedb_dir))
        
        # List available tables
        table_names = db.table_names()
        print(f"  Available LanceDB tables: {table_names}")
        
        # For now, use simplified approach - just load entities and community reports
        # The full GraphRAG indexer output structure is complex and may require
        # using the GraphRAG API's built-in loaders instead of manual parsing
        
        # Load entities
        entities_table = db.open_table("default-entity-description")
        entities_raw = entities_table.to_pandas()
        
        # Load community reports
        try:
            community_reports_table = db.open_table("default-community-full_content")
            community_reports_raw = community_reports_table.to_pandas()
            print(f"  ✓ Loaded {len(community_reports_raw)} community reports from LanceDB")
        except Exception as e:
            print(f"  ⚠️ No community reports table found: {e}")
            community_reports_raw = pd.DataFrame()
        
        # Load text units
        try:
            text_units_table = db.open_table("default-text_unit-text")
            text_units_raw = text_units_table.to_pandas()
            print(f"  ✓ Loaded {len(text_units_raw)} text units from LanceDB")
        except Exception as e:
            print(f"  ⚠️ No text units table found: {e}")
            text_units_raw = pd.DataFrame()
        
        print(f"  ✓ Loaded {len(entities_raw)} entities from LanceDB")
        
        # Parse attributes JSON to extract entity metadata
        # LanceDB stores: id, text (description), vector (embedding), attributes (JSON with title, etc.)
        if 'attributes' in entities_raw.columns:
            # Parse JSON attributes
            entities_raw['attrs'] = entities_raw['attributes'].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x
            )
            # Extract fields from attributes
            entities_raw['title'] = entities_raw['attrs'].apply(lambda x: x.get('title', '') if isinstance(x, dict) else '')
            entities_raw['description'] = entities_raw['text']  # The main text column is the description
            entities_raw['description_embedding'] = entities_raw['vector'].apply(lambda x: x.tolist() if hasattr(x, 'tolist') else x)
        
        # Store simplified data for querying
        # For global search, we mainly need community reports
        # For local search, we need entities and their embeddings
        self._entities = []  # Simplified - not using full Entity objects
        self._relationships = []
        self._text_units = []
        self._covariates = []
        
        # Parse community reports for global search
        if not community_reports_raw.empty:
            self._reports = []
            for _, row in community_reports_raw.iterrows():
                # Parse attributes if present
                attrs = {}
                if 'attributes' in row and row['attributes']:
                    try:
                        attrs = json.loads(row['attributes']) if isinstance(row['attributes'], str) else row['attributes']
                    except:
                        pass
                
                # Create a simplified report structure
                self._reports.append({
                    'id': row['id'],
                    'title': attrs.get('title', ''),
                    'content': row['text'],
                    'embedding': row['vector'].tolist() if hasattr(row['vector'], 'tolist') else row['vector']
                })
        else:
            self._reports = []
        
        print(f"  ✓ Parsed {len(self._reports)} community reports")
        print(f"  ✓ Parsed {len(entities_raw)} entities")
        
        # Setup entity embedding store (LanceDB)
        schema_config = VectorStoreSchemaConfig(
            id_field="id",
            vector_field="vector",
            text_field="text",
            attributes_field="attributes",
            vector_size=1536,  # text-embedding-3-small dimension
            index_name="default-entity-description"
        )
        
        self._description_embedding_store = LanceDBVectorStore(
            vector_store_schema_config=schema_config,
            collection_name="default-entity-description",
        )
        self._description_embedding_store.connect(db_uri=str(self.lancedb_dir))
        
        # Store raw dataframes for custom querying
        self._entities_df = entities_raw
        self._community_reports_df = community_reports_raw
        self._text_units_df = text_units_raw
        
        print("  ✓ Connected to entity embedding store")
    
    def _setup_local_search(self):
        """Setup local search engine - not implemented for simplified version."""
        self._load_data()
        print("  ℹ️ Local search not available (requires full GraphRAG indexer output)")
        self._local_search_engine = "not_available"
    
    def _setup_global_search(self):
        """Setup global search engine - simplified version using community reports directly."""
        if self._global_search_engine is not None:
            return
        
        self._load_data()
        
        # Simplified: Just use the community reports for global search
        print("  ℹ️ Using simplified global search (community report search)")
        self._global_search_engine = "simplified"
        
        print("✓ Global search engine ready (simplified)")
    
    async def local_search(self, query: str) -> dict:
        """
        Execute local search for entity-specific queries.
        
        Best for:
        - Specific contract clauses
        - Party obligations
        - Detailed contractual relationships
        - Precise information retrieval
        """
        self._setup_local_search()
        
        # Simplified version: fallback to global search
        if self._local_search_engine == "not_available":
            print("  → Falling back to global search")
            return await self.global_search(query)
        
        result = await self._local_search_engine.asearch(query)
        
        return {
            "query": query,
            "search_type": "local",
            "response": result.response,
            "context_data": getattr(result, "context_data", {}),
            "context_text": getattr(result, "context_text", ""),
            "completion_time": getattr(result, "completion_time", 0),
            "llm_calls": getattr(result, "llm_calls", 0),
        }
    
    async def global_search(self, query: str) -> dict:
        """
        Execute global search for high-level queries.
        
        Best for:
        - Cross-contract patterns
        - Industry trends
        - Risk summaries
        - Comparative analysis
        """
        self._setup_global_search()
        
        # Simplified version: search community reports directly
        if self._global_search_engine == "simplified":
            # Search through community reports
            relevant_reports = []
            for report in self._reports[:10]:  # Top 10 reports
                relevant_reports.append(report['content'])
            
            # Combine reports as context
            context = "\n\n".join(relevant_reports)
            
            # Use LLM to answer based on context
            prompt = f"""Based on the following contract analysis reports, answer this question:

Question: {query}

Reports:
{context}

Provide a comprehensive answer based on the reports above."""
            
            # Simple completion call
            from openai import OpenAI
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
            )
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.llm_deployment,
                max_completion_tokens=2000
            )
            
            answer = response.choices[0].message.content
            
            return {
                "query": query,
                "search_type": "global",
                "response": answer,
                "context_data": {"num_reports": len(relevant_reports)},
                "context_text": context[:1000] + "..." if len(context) > 1000 else context,
                "completion_time": 0,
                "llm_calls": 1,
                "map_responses": [],
            }
        
        result = await self._global_search_engine.asearch(query)
        
        return {
            "query": query,
            "search_type": "global",
            "response": result.response,
            "context_data": getattr(result, "context_data", {}),
            "context_text": getattr(result, "context_text", ""),
            "completion_time": getattr(result, "completion_time", 0),
            "llm_calls": getattr(result, "llm_calls", 0),
            "map_responses": getattr(result, "map_responses", []),
        }
    
    async def hybrid_search(self, query: str, search_type: Literal["auto", "local", "global"] = "auto") -> dict:
        """
        Execute hybrid search with automatic routing.
        
        Args:
            query: The search query
            search_type: "auto" (decide based on query), "local", or "global"
        """
        # Auto-detect search type based on query characteristics
        if search_type == "auto":
            # Keywords suggesting global search
            global_keywords = [
                "all contracts", "across contracts", "overall", "trend", "pattern",
                "compare", "comparison", "summary", "overview", "industry",
                "common", "typical", "generally", "most", "least"
            ]
            
            query_lower = query.lower()
            if any(keyword in query_lower for keyword in global_keywords):
                search_type = "global"
            else:
                search_type = "local"
        
        # Execute appropriate search
        if search_type == "global":
            return await self.global_search(query)
        else:
            return await self.local_search(query)
    
    def query(self, query_text: str, search_type: Literal["auto", "local", "global"] = "auto") -> dict:
        """Synchronous wrapper for hybrid search."""
        return asyncio.run(self.hybrid_search(query_text, search_type))


# Convenience functions for direct use
def query_graphrag(query: str, search_type: Literal["auto", "local", "global"] = "auto") -> dict:
    """Query GraphRAG knowledge graph."""
    agent = GraphRAGAgent()
    return agent.query(query, search_type)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python graphrag_agent.py '<query>' [local|global|auto]")
        sys.exit(1)
    
    query_text = sys.argv[1]
    search_type_arg = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    print(f"🔍 GraphRAG Query: {query_text}")
    print(f"   Search Type: {search_type_arg}\n")
    
    result = query_graphrag(query_text, search_type_arg)
    
    print("\n" + "=" * 70)
    print(f"Search Type: {result['search_type'].upper()}")
    print("=" * 70)
    print(result['response'])
    print("\n" + "=" * 70)
    print(f"⏱️ Completed in {result['completion_time']:.2f}s")
    print(f"🤖 LLM Calls: {result['llm_calls']}")
