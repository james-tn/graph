from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Literal
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends

# Load environment variables from .env file
load_dotenv()

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.agents.router_agent import RouterAgent
from backend.app.core.auth import get_current_user, get_user_email
from backend.app.core.auth import get_current_user, get_user_email

app = FastAPI(
    title="Contract Intelligence API - Hybrid Search",
    description="Hybrid graph search combining PostgreSQL and Microsoft GraphRAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize router agent
router_agent = RouterAgent()

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    strategy: Optional[Literal["auto", "postgres", "graphrag", "hybrid"]] = "auto"

class QueryResponse(BaseModel):
    query: str
    routing: dict
    postgres_result: Optional[dict] = None
    graphrag_result: Optional[dict] = None
    unified_response: str
    sources: list

class IngestRequest(BaseModel):
    run_postgres: bool = True
    run_graphrag: bool = True

class IngestResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Contract Intelligence Hybrid Search",
        "postgres": "available",
        "graphrag": "available",
    }


# Main query endpoint
@app.post("/api/query", response_model=QueryResponse)
async def query_contracts(
    request: QueryRequest,
    user: dict = Depends(get_current_user)
):
    """
    Execute hybrid search query with intelligent routing.
    
    - **query**: The search query text
    - **strategy**: Routing strategy ("auto", "postgres", "graphrag", or "hybrid")
    """
    try:
        # Route query through router agent
        strategy_map = {
            "auto": None,
            "postgres": "postgres",
            "graphrag": "graphrag",
            "hybrid": "hybrid"
        }
        
        result = await router_agent.route_query(
            request.query,
            force_strategy=strategy_map.get(request.strategy)
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


# Ingestion endpoint
@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_contracts(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """
    Trigger dual ingestion pipeline (PostgreSQL + GraphRAG).
    
    - **run_postgres**: Whether to run PostgreSQL ingestion
    - **run_graphrag**: Whether to run GraphRAG indexing
    """
    try:
        # For now, return instructions (background ingestion would be added later)
        if request.run_postgres and request.run_graphrag:
            message = "Run: python backend/ingestion.py (ingests to both PostgreSQL and GraphRAG)"
        elif request.run_postgres:
            message = "PostgreSQL ingestion: python backend/ingestion.py (comment out GraphRAG section)"
        elif request.run_graphrag:
            message = "GraphRAG indexing: graphrag index --root . --config graphrag_config"
        else:
            return IngestResponse(status="skipped", message="No ingestion requested")
        
        return IngestResponse(
            status="pending",
            message=message,
            task_id=None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


# Get routing analysis (without executing query)
@app.post("/api/analyze")
async def analyze_query(
    request: QueryRequest,
    user: dict = Depends(get_current_user)
):
    """
    Analyze query routing without executing the search.
    
    Returns routing decision and reasoning.
    """
    try:
        routing = router_agent.analyze_query(request.query)
        return routing
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Statistics endpoint
@app.get("/api/stats")
async def get_statistics(user: dict = Depends(get_current_user)):
    """Get database and index statistics."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        DB_HOST = os.environ.get("POSTGRES_HOST", "ci-ci-dev-pgflex.postgres.database.azure.com")
        DB_NAME = os.environ.get("POSTGRES_DATABASE", "cipgraph")
        DB_USER = os.environ.get("POSTGRES_USER", "pgadmin")
        DB_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require',
            cursor_factory=RealDictCursor
        )
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) as count FROM contracts")
        contract_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM clauses")
        clause_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM parties")
        party_count = cur.fetchone()['count']
        
        cur.close()
        conn.close()
        
        # Check GraphRAG output
        graphrag_indexed = False
        graphrag_entities = 0
        graphrag_output = Path("data/output/create_final_entities.parquet")
        if graphrag_output.exists():
            graphrag_indexed = True
            try:
                import pandas as pd
                entities_df = pd.read_parquet(graphrag_output)
                graphrag_entities = len(entities_df)
            except:
                pass
        
        return {
            "postgres": {
                "contracts": contract_count,
                "clauses": clause_count,
                "parties": party_count,
            },
            "graphrag": {
                "indexed": graphrag_indexed,
                "entities": graphrag_entities,
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


# ==================== SERVE REACT FRONTEND ====================
# Mount static files for production deployment (when running in Docker)
frontend_dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    # Mount static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_path / "assets")), name="assets")
    
    # Serve index.html for root and all non-API routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React frontend for all non-API routes."""
        # Don't serve frontend for API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (React Router handles client-side routing)
        index_file = frontend_dist_path / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not built")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
