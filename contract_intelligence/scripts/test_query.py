import asyncio
import pandas as pd
from pathlib import Path
from graphrag.config.load_config import load_config
from graphrag.api.query import drift_search
from graphrag.config.models.graph_rag_config import GraphRagConfig
import graphrag.query.structured_search.drift_search.primer as primer_module

# Patch the prompt to use double quotes for JSON keys to avoid JSONDecodeError
primer_module.DRIFT_PRIMER_PROMPT = """You are a helpful agent designed to reason over a knowledge graph in response to a user query.
This is a unique knowledge graph where edges are freeform text rather than verb operators. You will begin your reasoning looking at a summary of the content of the most relevant communites and will provide:

1. score: How well the intermediate answer addresses the query. A score of 0 indicates a poor, unfocused answer, while a score of 100 indicates a highly focused, relevant answer that addresses the query in its entirety.

2. intermediate_answer: This answer should match the level of detail and length found in the community summaries. The intermediate answer should be exactly 2000 characters long. This must be formatted in markdown and must begin with a header that explains how the following text is related to the query.

3. follow_up_queries: A list of follow-up queries that could be asked to further explore the topic. These should be formatted as a list of strings. Generate at least five good follow-up queries.

Use this information to help you decide whether or not you need more information about the entities mentioned in the report. You may also use your general knowledge to think of entities which may help enrich your answer.

You will also provide a full answer from the content you have available. Use the data provided to generate follow-up queries to help refine your search. Do not ask compound questions, for example: "What is the market cap of Apple and Microsoft?". Use your knowledge of the entity distribution to focus on entity types that will be useful for searching a broad area of the knowledge graph.

For the query:

{query}

The top-ranked community summaries:

{community_reports}

Provide the intermediate answer, and all scores in JSON format following:

{{"intermediate_answer": str,
"score": int,
"follow_up_queries": List[str]}}

Begin:
"""

async def run_queries():
    root_dir = Path.cwd()
    config_path = root_dir / "graphrag_config" / "settings.yaml"
    
    print(f"Loading config from {config_path}")
    config = load_config(root_dir=root_dir, config_filepath=config_path)
    
    output_dir = root_dir / "data" / "output"
    print(f"Reading data from {output_dir}")
    
    # Read parquet files
    entities = pd.read_parquet(output_dir / "entities.parquet")
    communities = pd.read_parquet(output_dir / "communities.parquet")
    community_reports = pd.read_parquet(output_dir / "community_reports.parquet")
    text_units = pd.read_parquet(output_dir / "text_units.parquet")
    relationships = pd.read_parquet(output_dir / "relationships.parquet")
    
    query = "What are the obligations of the Vendor?"
    
    print(f"\n--- Running DRIFT Search for query: '{query}' ---")
    try:
        response, context = await drift_search(
            config=config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units=text_units,
            relationships=relationships,
            community_level=2,
            response_type="Multiple Paragraphs",
            query=query,
        )
        print("DRIFT Search Response:")
        print(response)
        
        print("\n--- Context Data (Provenance) ---")
        if isinstance(context, dict):
            for key, value in context.items():
                print(f"Key: {key}")
                if isinstance(value, pd.DataFrame):
                    print(f"  Shape: {value.shape}")
                    print(f"  Columns: {value.columns.tolist()}")
                    print(f"  Head:\n{value.head(2)}")
                else:
                    print(f"  Value: {value}")
        else:
            print(f"Context type: {type(context)}")
            print(context)

    except Exception as e:
        print(f"DRIFT Search failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_queries())
