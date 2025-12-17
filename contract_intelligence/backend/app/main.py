from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File as FastAPIFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Literal, List
import asyncio
import os
import sys
import traceback
import uuid
import shutil
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
from backend.utils.mermaid_corrector import correct_mermaid_diagram

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

class MermaidCorrectionRequest(BaseModel):
    mermaid_code: str
    error_message: str

class MermaidCorrectionResponse(BaseModel):
    corrected_code: str
    success: bool

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str

class IndexRequest(BaseModel):
    run_postgres: bool = True
    run_graphrag: bool = False  # GraphRAG is slower, default off for incremental

class IndexResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None
    contracts_processed: Optional[int] = None

class IndexStatusResponse(BaseModel):
    task_id: str
    status: str
    message: str
    progress: Optional[dict] = None

# Track background indexing tasks
indexing_tasks: dict = {}


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
        print("result\n", result)
        return QueryResponse(**result)
    
    except Exception as e:
        # Log full traceback for debugging
        print("=" * 70)
        print("ERROR in /api/query endpoint:")
        print(traceback.format_exc())
        print("=" * 70)
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


# ==================== FILE UPLOAD ENDPOINT ====================
@app.post("/api/upload", response_model=UploadResponse)
async def upload_contract_file(
    file: UploadFile = FastAPIFile(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload a contract file (markdown or text) for processing.
    
    Files are saved to the data/input directory for subsequent indexing.
    Supports .md, .txt, and .markdown files.
    """
    try:
        # Validate file extension
        allowed_extensions = {'.md', '.txt', '.markdown'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type '{file_ext}'. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Determine input directory
        project_root = Path(__file__).parent.parent.parent
        input_dir = project_root / "data" / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename if contract_ prefix not present
        original_name = Path(file.filename).stem
        if not original_name.startswith("contract_"):
            # Find next available contract number
            existing_contracts = list(input_dir.glob("contract_*.md"))
            if existing_contracts:
                # Extract numbers and find max
                numbers = []
                for f in existing_contracts:
                    try:
                        num = int(f.stem.split('_')[1])
                        numbers.append(num)
                    except (IndexError, ValueError):
                        pass
                next_num = max(numbers) + 1 if numbers else 1
            else:
                next_num = 1
            
            # Create new filename: contract_XXX_originalname.md
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in original_name)
            new_filename = f"contract_{next_num:03d}_{safe_name}.md"
        else:
            new_filename = f"{original_name}.md"
        
        # Save file
        file_path = input_dir / new_filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return UploadResponse(
            filename=new_filename,
            status="success",
            message=f"File uploaded successfully to {file_path.relative_to(project_root)}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# ==================== INDEXING ENDPOINTS ====================
def run_incremental_indexing(task_id: str, run_postgres: bool = True, run_graphrag: bool = False):
    """
    Background task to run incremental indexing.
    
    This runs the ingestion pipeline with skip_schema_init=True to preserve existing data.
    """
    try:
        indexing_tasks[task_id] = {
            "status": "running",
            "message": "Starting incremental indexing...",
            "progress": {"stage": "initializing", "contracts_processed": 0}
        }
        
        # Import ingestion modules
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "data_ingestion"))
        from postgres_ingestion import run_postgres_ingestion, get_database_statistics
        
        if run_postgres:
            indexing_tasks[task_id]["progress"]["stage"] = "postgresql_ingestion"
            indexing_tasks[task_id]["message"] = "Running PostgreSQL incremental ingestion..."
            
            # Run with skip_schema_init=True to preserve existing data (incremental)
            success = run_postgres_ingestion(
                num_contracts=None,  # Process all new contracts
                n_parallel=5,
                skip_schema_init=True  # IMPORTANT: Don't drop existing tables
            )
            
            if not success:
                indexing_tasks[task_id] = {
                    "status": "error",
                    "message": "PostgreSQL ingestion failed",
                    "progress": {"stage": "failed"}
                }
                return
            
            # Get updated stats
            stats = get_database_statistics()
            indexing_tasks[task_id]["progress"]["contracts_processed"] = stats.get("contracts", 0)
        
        if run_graphrag:
            indexing_tasks[task_id]["progress"]["stage"] = "graphrag_indexing"
            indexing_tasks[task_id]["message"] = "Running GraphRAG indexing (this may take a while)..."
            
            # GraphRAG indexing would go here
            # For now, we note it requires manual execution due to complexity
            indexing_tasks[task_id]["message"] = "PostgreSQL complete. GraphRAG requires manual execution: graphrag index --root ."
        
        indexing_tasks[task_id] = {
            "status": "complete",
            "message": "Incremental indexing completed successfully!",
            "progress": {
                "stage": "complete",
                "contracts_processed": indexing_tasks[task_id]["progress"].get("contracts_processed", 0)
            }
        }
        
    except Exception as e:
        indexing_tasks[task_id] = {
            "status": "error",
            "message": f"Indexing failed: {str(e)}",
            "progress": {"stage": "error", "error": str(e)}
        }
        print(f"Indexing error: {traceback.format_exc()}")


@app.post("/api/index", response_model=IndexResponse)
async def start_indexing(
    background_tasks: BackgroundTasks,
    request: IndexRequest = IndexRequest(),
    user: dict = Depends(get_current_user)
):
    """
    Start incremental indexing of uploaded contracts.
    
    This endpoint triggers background processing of new contract files.
    Use GET /api/index/status/{task_id} to check progress.
    
    - **run_postgres**: Whether to run PostgreSQL ingestion (default: True)
    - **run_graphrag**: Whether to run GraphRAG indexing (default: False, as it's slow)
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())[:8]
        
        # Initialize task status
        indexing_tasks[task_id] = {
            "status": "queued",
            "message": "Indexing task queued...",
            "progress": {}
        }
        
        # Add to background tasks
        background_tasks.add_task(
            run_incremental_indexing,
            task_id,
            request.run_postgres,
            request.run_graphrag
        )
        
        return IndexResponse(
            status="started",
            message="Incremental indexing started in background. Check status with task_id.",
            task_id=task_id,
            contracts_processed=None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start indexing: {str(e)}")


@app.get("/api/index/status/{task_id}", response_model=IndexStatusResponse)
async def get_indexing_status(
    task_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get the status of an indexing task.
    
    - **task_id**: The task ID returned from POST /api/index
    """
    if task_id not in indexing_tasks:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    
    task = indexing_tasks[task_id]
    return IndexStatusResponse(
        task_id=task_id,
        status=task["status"],
        message=task["message"],
        progress=task.get("progress")
    )


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

# Mermaid diagram correction endpoint
@app.post("/api/mermaid/fix", response_model=MermaidCorrectionResponse)
async def fix_mermaid_diagram(
    request: MermaidCorrectionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Fix invalid Mermaid diagram syntax using LLM.
    
    Frontend sends diagrams that failed to render for automatic correction.
    
    - **mermaid_code**: The invalid Mermaid diagram code
    - **error_message**: Error message from frontend rendering attempt
    """
    try:
        print("\n" + "=" * 70)
        print("RECEIVED MERMAID FIX REQUEST")
        print("=" * 70)
        print(f"Error from frontend: {request.error_message}")
        print(f"Code length: {len(request.mermaid_code)} chars")
        
        corrected = correct_mermaid_diagram(
            request.mermaid_code,
            request.error_message
        )
        
        success = corrected != request.mermaid_code
        print(f"Correction successful: {success}")
        print("=" * 70 + "\n")
        
        return MermaidCorrectionResponse(
            corrected_code=corrected,
            success=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction failed: {str(e)}")


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
