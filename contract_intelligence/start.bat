@echo off
REM Contract Intelligence Platform - Main Startup Script

echo ======================================================================
echo Contract Intelligence Platform
echo ======================================================================
echo.
echo This will run the complete pipeline:
echo   1. Ingest contracts with LLM extraction
echo   2. Build Apache AGE graph with relationships
echo   3. Run AI agent with natural language queries
echo.
echo Make sure environment variables are set:
echo   - POSTGRES_ADMIN_PASSWORD
echo   - AZURE_OPENAI_API_KEY
echo   - AZURE_OPENAI_ENDPOINT
echo   - AZURE_OPENAI_DEPLOYMENT_NAME
echo   - EMBEDDING_DEPLOYMENT_NAME
echo.
pause

REM Load environment variables from .env file
if exist .env (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=1* delims==" %%a in (".env") do (
        set "%%a=%%b"
    )
    echo.
)

echo ======================================================================
echo Step 1: Contract Ingestion with LLM
echo ======================================================================
echo Extracting contracts, parties, clauses, obligations, rights, terms...
echo This may take 2-3 minutes for 5 contracts with parallel processing.
echo.

uv run backend\ingestion.py
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Ingestion failed!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Step 2: Apache AGE Graph Creation
echo ======================================================================
echo Building graph nodes and relationships...
echo.

uv run backend\build_graph.py
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Graph creation failed!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Step 3: AI Agent with Graph Traversal
echo ======================================================================
echo Running demo queries with SQL, vector search, and graph traversal...
echo.

uv run backend\agents\contract_agent.py
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Agent execution failed!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo ✅ SUCCESS! Contract Intelligence Platform Ready
echo ======================================================================
echo.
echo The system is now operational with:
echo   ✓ Comprehensive entity extraction (obligations, rights, terms)
echo   ✓ Apache AGE graph with multi-hop relationships
echo   ✓ AI agent with SQL, vector search, and graph traversal
echo.
echo Example queries you can now ask:
echo   - "What obligations does Acme Corp have?"
echo   - "Show me all rights granted to vendors"
echo   - "Analyze the complete relationship network for contract_000"
echo   - "Find clauses about data protection"
echo   - "What are the high-risk clauses?"
echo.
pause
