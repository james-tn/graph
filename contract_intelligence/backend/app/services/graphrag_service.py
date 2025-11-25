import asyncio
import pandas as pd
from pathlib import Path
from graphrag.config.load_config import load_config
from graphrag.api.query import drift_search
from graphrag.api import build_index
import graphrag.query.structured_search.drift_search.primer as primer_module
import logging
import shutil

# Patch the prompt (as done in the script)
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

logger = logging.getLogger(__name__)

class GraphRAGService:
    def __init__(self):
        self.root_dir = Path("c:/testing/graph/contract_intelligence")
        self.config_path = self.root_dir / "graphrag_config" / "settings.yaml"
        self.input_dir = self.root_dir / "data" / "input"
        self.output_dir = self.root_dir / "data" / "output"

    async def save_file(self, file_content: bytes, filename: str):
        self.input_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.input_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        return str(file_path)

    async def run_ingestion(self):
        logger.info("Starting ingestion...")
        config = load_config(root_dir=self.root_dir, config_filepath=self.config_path)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        await build_index(
            config=config,
            run_id="api-run",
            is_resume_run=False,
            memory_profile=False,
            progress_reporter=None,
            emit=None,
            opentelemetry_reporter=None,
        )
        logger.info("Ingestion complete.")

    async def query(self, query_text: str):
        logger.info(f"Running query: {query_text}")
        config = load_config(root_dir=self.root_dir, config_filepath=self.config_path)
        
        # Load data
        try:
            entities = pd.read_parquet(self.output_dir / "entities.parquet")
            communities = pd.read_parquet(self.output_dir / "communities.parquet")
            community_reports = pd.read_parquet(self.output_dir / "community_reports.parquet")
            text_units = pd.read_parquet(self.output_dir / "text_units.parquet")
            relationships = pd.read_parquet(self.output_dir / "relationships.parquet")
        except FileNotFoundError:
            return {"error": "Index not found. Please run ingestion first."}

        response, context = await drift_search(
            config=config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units=text_units,
            relationships=relationships,
            community_level=2,
            response_type="Multiple Paragraphs",
            query=query_text,
        )
        
        # Process context for frontend
        sources = []
        if isinstance(context, dict) and "sources" in context:
            sources_df = context["sources"]
            if isinstance(sources_df, pd.DataFrame):
                sources = sources_df.to_dict(orient="records")
        
        return {
            "answer": response,
            "sources": sources
        }

graphrag_service = GraphRAGService()
