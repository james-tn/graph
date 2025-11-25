"""Test script to debug GraphRAG query issues."""
import sys
import traceback
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    print("=" * 70)
    print("Testing GraphRAG Agent Query")
    print("=" * 70)
    
    from agents.graphrag_agent import GraphRAGAgent
    
    print("\n1. Creating GraphRAGAgent instance...")
    agent = GraphRAGAgent()
    
    print(f"\n   API Base: {agent.api_base}")
    print(f"   LLM Deployment: {agent.llm_deployment}")
    print(f"   Embedding Deployment: {agent.embedding_deployment}")
    
    print("\n2. Testing query...")
    query = "What are common risk patterns?"
    print(f"   Query: {query}")
    
    result = agent.query(query, search_type="global")
    print("result: ", result)
    
    print("\n3. Result:")
    print(f"   Answer: {result.get('response', 'No answer')[:200]}...")
    print(f"   Sources count: {len(result.get('sources', []))}")
    
    print("\n✓ Test completed successfully!")
    
except Exception as e:
    print(f"\n✗ Error occurred:")
    print(f"   {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
