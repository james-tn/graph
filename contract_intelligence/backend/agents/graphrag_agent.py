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
        """Load GraphRAG indexed data from parquet files (GraphRAG 2.x format)."""
        if self._entities is not None:
            return  # Already loaded
        
        print("📚 Loading GraphRAG data from storage...")
        
        import pandas as pd
        
        # GraphRAG 2.7.0 writes parquet files directly to output directory
        if not self.output_dir.exists():
            print(f"  ⚠️ Output directory not found: {self.output_dir}")
            print("  Please run GraphRAG indexing first")
            raise FileNotFoundError(f"GraphRAG output not found at {self.output_dir}")
        
        # Load parquet files
        print(f"  Loading from {self.output_dir}")
        
        # Load entities
        entities_path = self.output_dir / "entities.parquet"
        if entities_path.exists():
            entities_df = pd.read_parquet(entities_path)
            print(f"  ✓ Loaded {len(entities_df)} entities")
        else:
            print(f"  ⚠️ Entities file not found: {entities_path}")
            entities_df = pd.DataFrame()
        
        # Load relationships  
        relationships_path = self.output_dir / "relationships.parquet"
        if relationships_path.exists():
            relationships_df = pd.read_parquet(relationships_path)
            print(f"  ✓ Loaded {len(relationships_df)} relationships")
        else:
            print(f"  ⚠️ Relationships file not found: {relationships_path}")
            relationships_df = pd.DataFrame()
        
        # Load communities
        communities_path = self.output_dir / "communities.parquet"
        if communities_path.exists():
            communities_df = pd.read_parquet(communities_path)
            print(f"  ✓ Loaded {len(communities_df)} communities")
        else:
            print(f"  ⚠️ Communities file not found: {communities_path}")
            communities_df = pd.DataFrame()
        
        # Load community reports
        reports_path = self.output_dir / "community_reports.parquet"
        if reports_path.exists():
            reports_df = pd.read_parquet(reports_path)
            print(f"  ✓ Loaded {len(reports_df)} community reports")
        else:
            print(f"  ⚠️ Community reports file not found: {reports_path}")
            reports_df = pd.DataFrame()
        
        # Load text units
        text_units_path = self.output_dir / "text_units.parquet"
        if text_units_path.exists():
            text_units_df = pd.read_parquet(text_units_path)
            print(f"  ✓ Loaded {len(text_units_df)} text units")
        else:
            print(f"  ⚠️ Text units file not found: {text_units_path}")
            text_units_df = pd.DataFrame()
        
        # Load covariates (claims) if available
        covariates_path = self.output_dir / "covariates.parquet"
        if covariates_path.exists():
            covariates_df = pd.read_parquet(covariates_path)
            print(f"  ✓ Loaded {len(covariates_df)} covariates")
        else:
            print(f"  ℹ️ No covariates file (optional)")
            covariates_df = pd.DataFrame()
        
        # Convert to GraphRAG data model objects using indexer adapters
        from graphrag.query.indexer_adapters import (
            read_indexer_covariates,
            read_indexer_entities,
            read_indexer_relationships,
            read_indexer_reports,
            read_indexer_text_units,
        )
        
        # Set community level (use max level available)
        community_level = int(communities_df["level"].max()) if not communities_df.empty else 0
        print(f"  ℹ️ Using community level: {community_level}")
        
        # Parse data using GraphRAG's built-in adapters
        self._entities = read_indexer_entities(entities_df, communities_df, community_level) if not entities_df.empty else []
        self._relationships = read_indexer_relationships(relationships_df) if not relationships_df.empty else []
        self._reports = read_indexer_reports(reports_df, communities_df, community_level) if not reports_df.empty else []
        self._text_units = read_indexer_text_units(text_units_df) if not text_units_df.empty else []
        self._covariates = read_indexer_covariates(covariates_df) if not covariates_df.empty else []
        self._communities = communities_df
        
        print(f"  ✓ Parsed {len(self._entities)} entities")
        print(f"  ✓ Parsed {len(self._relationships)} relationships")
        print(f"  ✓ Parsed {len(self._reports)} community reports")
        print(f"  ✓ Parsed {len(self._text_units)} text units")
        print(f"  ✓ Parsed {len(self._covariates)} covariates")
        
        # Setup entity embedding store (LanceDB)
        from graphrag.vector_stores.lancedb import LanceDBVectorStore
        from graphrag.config.models.vector_store_schema_config import VectorStoreSchemaConfig
        
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
        
        print("  ✓ Connected to entity embedding store")
    
    def _setup_local_search(self):
        """Setup local search engine using GraphRAG factory."""
        self._load_data()
        
        if not self._entities:
            print("  ⚠️ No entities loaded, cannot setup local search")
            self._local_search_engine = "not_available"
            return
        
        print("  Setting up local search engine...")
        
        try:
            from graphrag.query.factory import get_local_search_engine
            from graphrag.config.models.graph_rag_config import GraphRagConfig
            
            # Load GraphRAG config
            from graphrag.config.load_config import load_config
            config_dir = self.root_dir / "graphrag_config"
            config = load_config(config_dir)
            
            print(f"  Config loaded, creating search engine...")
            print(f"  Entities: {len(self._entities)}, Reports: {len(self._reports)}")
            
            # Create local search engine using GraphRAG factory
            self._local_search_engine = get_local_search_engine(
                config=config,
                reports=self._reports,
                text_units=self._text_units,
                entities=self._entities,
                relationships=self._relationships,
                covariates={"claims": self._covariates},
                response_type="concise with visualizations",  # Changed from "multiple paragraphs"
                description_embedding_store=self._description_embedding_store,
            )
            
            if self._local_search_engine is None:
                raise ValueError("get_local_search_engine returned None")
            
            print(f"  Local search engine ready: {type(self._local_search_engine)}")
            print(f"  Has search method: {hasattr(self._local_search_engine, 'search')}")
        except Exception as e:
            print(f"  Could not initialize local search: {e}")
            import traceback
            traceback.print_exc()
            print("  -> Will fall back to global search")
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
        
        # If local search setup failed, fallback to global search
        if self._local_search_engine == "not_available":
            print("  -> Falling back to global search")
            return await self.global_search(query)
        
        # Execute local search
        try:
            # LocalSearch.search() is async
            result = await self._local_search_engine.search(query)
            
            # Convert context_data to serializable format (GraphRAG returns DataFrames)
            context_data = getattr(result, "context_data", {})
            if context_data:
                serializable_context = {}
                for key, value in context_data.items():
                    if hasattr(value, 'to_dict'):  # pandas DataFrame
                        serializable_context[key] = value.to_dict('records')
                    else:
                        serializable_context[key] = value
                context_data = serializable_context
            
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
            print("  -> Falling back to global search")
            return await self.global_search(query)
    
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
            print(f"  Processing {len(self._reports)} community reports...")
            
            for i, report in enumerate(self._reports[:10]):  # Top 10 reports
                # CommunityReport objects have attributes, not dict keys
                # Try different attribute names
                report_text = None
                for attr in ['full_content', 'content', 'summary', 'title']:
                    report_text = getattr(report, attr, None)
                    if report_text:
                        break
                
                if report_text:
                    relevant_reports.append(report_text)
                    print(f"    Report {i}: {len(report_text)} chars")
                else:
                    print(f"    Report {i}: No content found. Available attrs: {dir(report)[:10]}")
            
            if not relevant_reports:
                return {
                    "query": query,
                    "search_type": "global",
                    "response": "No community reports available to answer this query. Please check if GraphRAG indexing completed successfully.",
                    "context_data": {},
                    "context_text": "",
                    "completion_time": 0,
                    "llm_calls": 0,
                }
            
            print(f"  Using {len(relevant_reports)} reports as context")
            
            # Combine reports as context
            context = "\n\n".join(relevant_reports)
            
            # Use LLM to answer based on context
            prompt = f"""Based on the following contract analysis reports, answer this question concisely with rich visualizations.

Question: {query}

Reports:
{context}

**CRITICAL INSTRUCTIONS - CONCISE & VISUAL:**

🎯 **BE BRIEF:** 
- Maximum 3-4 sentences of text explanation
- Let charts and diagrams do the talking
- Use bullet points, not paragraphs

📊 **VISUALIZE EVERYTHING:**
Ask yourself: "Can I show this as a chart instead of text?" If yes, DO IT.

**Mermaid Chart Types:**

1. **Pie Charts** - For distributions, proportions, breakdowns:
```mermaid
pie title Risk Distribution
    "High ⚠️" : 23
    "Medium ⚡" : 45
    "Low ✓" : 32
```

2. **Flow/Relationship Graphs** - For patterns, connections, hierarchies:
```mermaid
graph LR
    A[Pattern Type A] -->|leads to| B[Outcome 1]
    A -->|may cause| C[Outcome 2]
    D[Pattern Type B] -->|results in| B
    style A fill:#e1f5ff,stroke:#0066cc
    style B fill:#fff4e6,stroke:#ff9800
```

3. **Timelines** - For temporal patterns:
```mermaid
gantt
    title Contract Renewal Patterns
    dateFormat YYYY-MM
    section Q1
    Pattern A :2024-01, 2024-03
    section Q2
    Pattern B :2024-04, 2024-06
```

4. **Bar Charts** - For comparisons:
```mermaid
%%{{init: {{'theme':'dark'}}}}%%
xychart-beta
    title "Clause Type Frequency"
    x-axis [Liability, IP, Termination, Payment]
    y-axis "Count" 0 --> 50
    bar [45, 32, 28, 15]
```

5. **Mind Maps** - For thematic relationships:
```mermaid
mindmap
  root((Risk Themes))
    Financial
      Payment delays
      Penalty clauses
    Legal
      Liability caps
      Indemnification
    Operational
      Termination rights
      Service levels
```

**Formatting:**
- Use emojis: 📊 data, 🔍 finding, 💡 insight, ⚠️ risk, ✓ good, ❌ bad, 🎯 key point
- **Bold key numbers**: **85%**, **23 contracts**, **$1.2M**
- Tables ONLY if charts won't work
- 2-3 bullet points max before showing a chart

Provide a CONCISE, VISUAL answer with multiple charts."""
            
            try:
                # Simple completion call using Azure OpenAI
                from openai import OpenAI
                client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base,
                )
                
                print(f"  Calling LLM with {len(prompt)} chars of prompt...")
                
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.llm_deployment,
                    max_completion_tokens=8000  
                )
                
                answer = response.choices[0].message.content
                print(f"  LLM returned: {len(answer) if answer else 0} chars")
                
                if not answer:
                    print(f"  WARNING: Empty response from LLM!")
                    print(f"  Response object: {response}")
                    answer = "No response generated from the LLM."
                
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
            except Exception as e:
                print(f"  ❌ ERROR calling LLM: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                return {
                    "query": query,
                    "search_type": "global",
                    "response": f"Error generating response: {str(e)}",
                    "context_data": {"error": str(e), "error_type": type(e).__name__},
                    "context_text": "",
                    "completion_time": 0,
                    "llm_calls": 0,
                    "map_responses": [],
                }
        
        result = await self._global_search_engine.asearch(query)
        
        # Convert context_data to serializable format (GraphRAG returns DataFrames)
        context_data = getattr(result, "context_data", {})
        if context_data:
            serializable_context = {}
            for key, value in context_data.items():
                if hasattr(value, 'to_dict'):  # pandas DataFrame
                    serializable_context[key] = value.to_dict('records')
                else:
                    serializable_context[key] = value
            context_data = serializable_context
        
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
