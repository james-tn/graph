@echo off
REM Contract Intelligence - Hybrid Search Application
REM This script runs the dual ingestion pipeline and starts the hybrid search system

echo ======================================================================
echo Contract Intelligence - Hybrid Graph Search
echo PostgreSQL + Apache AGE + Microsoft GraphRAG
echo ======================================================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env file with required environment variables.
    echo See HYBRID_SEARCH_GUIDE.md for details.
    pause
    exit /b 1
)

echo Step 1: Dual Ingestion Pipeline
echo ======================================================================
echo This will ingest ALL contracts into:
echo   1. PostgreSQL with Apache AGE graph
echo   2. Microsoft GraphRAG knowledge graph
echo.
echo This may take 10-20 minutes depending on the number of contracts...
echo.

REM Run dual ingestion
uv run backend\ingestion.py

if errorlevel 1 (
    echo.
    echo ERROR: Ingestion failed!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Ingestion Complete!
echo ======================================================================
echo.
echo To start the hybrid search application:
echo.
echo   Terminal 1 (Backend):  cd backend\app ^&^& python main.py
echo   Terminal 2 (Frontend): cd frontend ^&^& npm run dev
echo.
echo Then open: http://localhost:5173
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo ======================================================================
pause
