#!/usr/bin/env python3
# Copyright (c). Microsoft. All rights reserved.

"""
Hybrid Router Agent for Contract Intelligence

Intelligently routes queries to the most appropriate backend:
- PostgreSQL Agent: Structured queries, precise lookups, SQL capabilities
- GraphRAG Agent: Pattern discovery, cross-contract analysis, community insights
- Hybrid: Combines results from both sources when beneficial
"""

import asyncio
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

# Import our specialized agents
from backend.agents.contract_agent import ContractAgent
from backend.agents.graphrag_agent import GraphRAGAgent


class RouterAgent:
    """Intelligent query router for hybrid contract search."""
    
    # Query patterns for routing decisions
    POSTGRES_PATTERNS = [
        "specific contract", "contract identifier", "contract id",
        "party name", "party obligations", "party rights",
        "exact clause", "clause text", "keyword search",
        "monetary value", "payment", "fee", "price", "amount", "cost",
        "date", "deadline", "effective date", "expiration",
        "high risk", "risk level", "compliance",
        "list", "count", "statistics", "how many", "total", "sum",
        "which contracts", "find contract", "filter",
        "aggregate", "group by", "average", "maximum", "minimum",
        "top", "largest", "smallest", "most", "least",
        "quantitative", "metric", "measure", "calculation",
    ]
    
    GRAPHRAG_PATTERNS = [
        "pattern", "trend", "common themes", "typical language", "generally",
        "compare narratively", "qualitative comparison", "thematic difference",
        "thematic overview", "narrative summary", "abstractive summary",
        "industry practice", "best practice", "standard language",
        "relationship between", "connection", "related to",
        "theme", "conceptual category",
        "why", "how", "explain", "understand", "rationale",
        "insight", "implication", "strategic",
    ]
    
    def __init__(self):
        """Initialize router with access to both agents."""
        # Validate environment variables
        api_key = os.environ.get("GRAPHRAG_API_KEY")
        api_base = os.environ.get("GRAPHRAG_API_BASE")
        api_version = os.environ.get("GRAPHRAG_API_VERSION", "2024-02-15-preview")
        
        if not api_key:
            raise ValueError("GRAPHRAG_API_KEY environment variable is required")
        if not api_base:
            raise ValueError("GRAPHRAG_API_BASE environment variable is required")
        
        self.openai_client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=api_base
        )
        self.llm_model = os.environ.get("GRAPHRAG_LLM_DEPLOYMENT_NAME", "gpt-4o")
        
        # Get the project root directory (contract_intelligence/)
        # This file is in backend/agents/, so go up two levels
        project_root = Path(__file__).parent.parent.parent
        
        # Initialize specialized agents
        self.postgres_agent = ContractAgent()
        self.graphrag_agent = GraphRAGAgent(root_dir=project_root)
    
    def analyze_query(self, query: str) -> dict:
        """
        Analyze query to determine optimal routing strategy.
        
        Returns:
            {
                "strategy": "postgres" | "graphrag" | "hybrid",
                "reasoning": "Explanation of routing decision",
                "postgres_score": float,  # 0-1 confidence for PostgreSQL
                "graphrag_score": float,  # 0-1 confidence for GraphRAG
            }
        """
        query_lower = query.lower()
        
        # Calculate pattern match scores
        postgres_matches = sum(1 for pattern in self.POSTGRES_PATTERNS if pattern in query_lower)
        graphrag_matches = sum(1 for pattern in self.GRAPHRAG_PATTERNS if pattern in query_lower)
        
        postgres_score = postgres_matches / len(self.POSTGRES_PATTERNS)
        graphrag_score = graphrag_matches / len(self.GRAPHRAG_PATTERNS)
        
        # Use LLM for intelligent routing decision
        system_prompt = """You are a query router for a hybrid contract intelligence system.

You have access to two specialized search engines:

1. **PostgreSQL Agent** (Structured Database) - DEFAULT:
   - Precise lookups by contract ID, party name, or specific terms
   - SQL queries for exact filtering, counting, and aggregations
   - Quantitative analysis: totals, averages, counts, grouping
   - Vector similarity search on clause embeddings
   - Graph traversal using Apache AGE (party->contract->clause relationships)
   - Best for: specific contracts, exact matches, numerical queries, structured data, quantitative summaries, aggregations

2. **GraphRAG Agent** (Knowledge Graph) - SPECIALIZED:
   - Entity extraction with community detection
   - Cross-document thematic pattern analysis
   - Abstractive/qualitative summaries (narrative insights, not numbers)
   - Local search for entity-centric context
   - Best for: "why/how" questions, thematic analysis, qualitative comparisons, narrative insights, strategic implications
   - NOT for: counting, totals, averages, or any quantitative aggregation (use PostgreSQL instead)

**IMPORTANT**: Use PostgreSQL for ANY quantitative/numerical queries including counts, totals, averages, grouping. Only use GraphRAG for abstractive/qualitative/narrative analysis.

Analyze the query and decide which approach is best. Return JSON only:
{
  "strategy": "postgres" | "graphrag" | "hybrid",
  "reasoning": "One sentence explaining your decision",
  "primary_source": "postgres" | "graphrag" (for hybrid, which is primary)
}"""
        
        user_prompt = f"""Query: "{query}"

Pattern analysis:
- PostgreSQL indicators: {postgres_matches} matches
- GraphRAG indicators: {graphrag_matches} matches

Route this query."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            import json
            decision = json.loads(response.choices[0].message.content)
            
            return {
                "strategy": decision["strategy"],
                "reasoning": decision["reasoning"],
                "primary_source": decision.get("primary_source", decision["strategy"]),
                "postgres_score": postgres_score,
                "graphrag_score": graphrag_score,
            }
        
        except Exception as e:
            # Fallback to heuristic routing
            if postgres_score > graphrag_score:
                strategy = "postgres"
                reasoning = "Query appears to need structured database lookup"
            elif graphrag_score > postgres_score:
                strategy = "graphrag"
                reasoning = "Query requires knowledge graph analysis"
            else:
                strategy = "hybrid"
                reasoning = "Query could benefit from both approaches"
            
            return {
                "strategy": strategy,
                "reasoning": reasoning,
                "primary_source": strategy if strategy != "hybrid" else "graphrag",
                "postgres_score": postgres_score,
                "graphrag_score": graphrag_score,
            }
    
    async def route_query(self, query: str, force_strategy: str = None) -> dict:
        """
        Route query to appropriate agent(s) and return results.
        
        Args:
            query: User's search query
            force_strategy: Override routing decision ("postgres", "graphrag", or "hybrid")
        
        Returns:
            {
                "query": str,
                "routing": {...},  # Routing decision details
                "postgres_result": {...} | None,
                "graphrag_result": {...} | None,
                "unified_response": str,  # Combined answer
                "sources": [...]  # Source attribution
            }
        """
        # Determine routing strategy
        if force_strategy:
            routing = {
                "strategy": force_strategy,
                "reasoning": f"User forced {force_strategy} routing",
                "primary_source": force_strategy if force_strategy != "hybrid" else "graphrag",
                "postgres_score": 0.0,
                "graphrag_score": 0.0,
            }
        else:
            routing = self.analyze_query(query)
        
        strategy = routing["strategy"]
        
        # Execute queries based on strategy
        postgres_result = None
        graphrag_result = None
        
        if strategy == "postgres":
            # PostgreSQL only
            postgres_result = await self._query_postgres(query)
        
        elif strategy == "graphrag":
            # GraphRAG only
            graphrag_result = await self.graphrag_agent.hybrid_search(query)
        
        else:  # hybrid
            # Both sources (parallel execution)
            postgres_task = self._query_postgres(query)
            graphrag_task = self.graphrag_agent.hybrid_search(query)
            
            postgres_result, graphrag_result = await asyncio.gather(
                postgres_task, graphrag_task, return_exceptions=True
            )
            
            # Handle errors
            if isinstance(postgres_result, Exception):
                postgres_result = {"error": str(postgres_result)}
            if isinstance(graphrag_result, Exception):
                graphrag_result = {"error": str(graphrag_result)}
        
        # Generate unified response
        unified_response = self._generate_unified_response(
            query, routing, postgres_result, graphrag_result
        )
        
        # Compile sources
        sources = self._extract_sources(postgres_result, graphrag_result)
        
        return {
            "query": query,
            "routing": routing,
            "postgres_result": postgres_result,
            "graphrag_result": graphrag_result,
            "unified_response": unified_response,
            "sources": sources,
        }
    
    async def _query_postgres(self, query: str) -> dict:
        """Execute PostgreSQL agent query."""
        # The contract agent uses synchronous execution, wrap it
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.postgres_agent.query, query)
        return result
    
    def _generate_unified_response(
        self, query: str, routing: dict, postgres_result: dict, graphrag_result: dict
    ) -> str:
        """Generate a unified response combining results from both sources."""
        strategy = routing["strategy"]
        
        if strategy == "postgres" and postgres_result:
            if postgres_result.get("error"):
                return f"PostgreSQL query failed: {postgres_result['error']}"
            return postgres_result.get("response", "No response from PostgreSQL agent")
        
        elif strategy == "graphrag" and graphrag_result:
            if graphrag_result.get("error"):
                return f"GraphRAG query failed: {graphrag_result['error']}"
            return graphrag_result.get("response", "No response from GraphRAG agent")
        
        else:  # hybrid
            sections = []
            
            # Add routing explanation
            sections.append(f"**Hybrid Search Results** ({routing['reasoning']})\n")
            
            # GraphRAG section
            if graphrag_result and not graphrag_result.get("error"):
                sections.append("### Knowledge Graph Analysis (GraphRAG)")
                sections.append(graphrag_result.get("response", "No response"))
                sections.append("")
            
            # PostgreSQL section
            if postgres_result and not postgres_result.get("error"):
                sections.append("### Structured Database Query (PostgreSQL)")
                sections.append(postgres_result.get("response", "No response"))
                sections.append("")
            
            # Handle errors
            if postgres_result and postgres_result.get("error"):
                sections.append(f"*PostgreSQL query failed: {postgres_result['error']}*")
            if graphrag_result and graphrag_result.get("error"):
                sections.append(f"*GraphRAG query failed: {graphrag_result['error']}*")
            
            return "\n".join(sections)
    
    def _extract_sources(self, postgres_result: dict, graphrag_result: dict) -> list:
        """Extract source attributions from results."""
        sources = []
        
        if postgres_result and not postgres_result.get("error"):
            sources.append({
                "type": "postgres",
                "name": "PostgreSQL Database",
                "description": "Structured contract data with SQL and graph capabilities",
            })
        
        if graphrag_result and not graphrag_result.get("error"):
            search_type = graphrag_result.get("search_type", "unknown")
            sources.append({
                "type": "graphrag",
                "name": f"Microsoft GraphRAG ({search_type.title()} Search)",
                "description": "Knowledge graph with entity extraction and community detection",
            })
        
        return sources
    
    def query(self, query_text: str, force_strategy: str = None) -> dict:
        """Synchronous wrapper for route_query."""
        return asyncio.run(self.route_query(query_text, force_strategy))


# Convenience function
def hybrid_search(query: str, strategy: str = None) -> dict:
    """Execute hybrid search with intelligent routing."""
    router = RouterAgent()
    return router.query(query, strategy)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python router_agent.py '<query>' [postgres|graphrag|hybrid]")
        sys.exit(1)
    
    query_text = sys.argv[1]
    force_strategy = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔍 Hybrid Search Query: {query_text}")
    if force_strategy:
        print(f"   Forced Strategy: {force_strategy}")
    print("\n" + "=" * 70)
    
    result = hybrid_search(query_text, force_strategy)
    
    print(f"\n🧭 Routing Decision: {result['routing']['strategy'].upper()}")
    print(f"   Reasoning: {result['routing']['reasoning']}")
    print("\n" + "=" * 70)
    print("RESPONSE")
    print("=" * 70)
    print(result['unified_response'])
    print("\n" + "=" * 70)
    print(f"📚 Sources: {', '.join(s['name'] for s in result['sources'])}")
