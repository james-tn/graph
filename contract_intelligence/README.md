# Contract Intelligence Platform

Hybrid contract intelligence system combining **PostgreSQL + GraphRAG** with AI agents for natural language contract analysis.

## Architecture

```
PostgreSQL Agent ←→ Router Agent ←→ GraphRAG Agent
       ↓                                   ↓
   PostgreSQL                          GraphRAG
   + pgvector                      Knowledge Graph
   + Apache AGE
```

**Dual Backend Strategy:**
- **PostgreSQL**: Precise SQL queries, graph traversal, semantic search
- **GraphRAG**: Cross-document patterns, global insights, community detection
- **Router**: Auto-selects optimal backend or combines both

## Quick Start

### Prerequisites

1. **Azure PostgreSQL Flexible Server** with extensions:
   - `vector` (pgvector)
   - `age` (Apache AGE)
   - `pg_trgm` (full-text search)

2. **Azure OpenAI** with deployments:
   - LLM model (e.g., gpt-4.1)
   - Embedding model (e.g., text-embedding-3-small)

3. **Environment Variables**:
   ```bash
   set POSTGRES_ADMIN_PASSWORD=<your-password>
   set GRAPHRAG_API_KEY=<your-azure-openai-key>
   set GRAPHRAG_API_BASE=https://<your-instance>.openai.azure.com
   set GRAPHRAG_LLM_DEPLOYMENT_NAME=gpt-4.1
   set GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small
   ```

### Run the Application

**Backend:**
```bash
start_backend.bat
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 for the hybrid search interface.

## Key Features

- 🔍 **Hybrid Search**: Intelligently routes queries between PostgreSQL and GraphRAG
- 🤖 **AI Agents**: Natural language queries with tool selection
- 📊 **Contract Relationships**: Parent-child hierarchies (MSAs → SOWs → Amendments)
- 🔗 **Graph Traversal**: Multi-hop queries via Apache AGE
- 📈 **Semantic Search**: Vector similarity with pgvector (1536d embeddings)

## Example Queries

```
"Show contract hierarchy for MSA-ZEN-202403-197"
"Find all amendments to DPA-SUM-202502-324"
"What obligations does Acme Corp have?"
"Compare payment terms across all contracts"
```

## Project Structure

```
contract_intelligence/
├── data_ingestion/          # Dual ingestion pipeline
│   ├── contract_extractor.py
│   ├── postgres_ingestion.py
│   ├── graphrag_ingestion.py
│   └── ingestion_pipeline.py
├── backend/
│   ├── agents/              # PostgreSQL, GraphRAG, Router agents
│   └── app/                 # FastAPI backend
├── frontend/                # React UI with hybrid search
├── data/
│   ├── input/              # Contract markdown files
│   └── output/             # GraphRAG artifacts
└── graphrag_config/        # GraphRAG settings
```

## Database Schema

**Core Tables:**
- `contracts` - Contract metadata with `reference_number` (MSA-XXX-YYYYMM-NNN)
- `contract_relationships` - Parent-child links (MSAs, SOWs, amendments)
- `parties` - Legal entities with roles
- `clauses` - Sections with embeddings and risk levels
- `obligations` / `rights` - Extracted actions with parties

**Graph (Apache AGE):**
- Party → Contract → Clause → Obligation/Right relationships

## Agent Tools

**PostgreSQL Agent:**
- `execute_sql_query()` - SQL/Cypher with CTE and WITH RECURSIVE support
- `get_contract_family()` - Recursive hierarchy traversal
- Supports semantic search, graph queries, analytics

**GraphRAG Agent:**
- Local search (entity-centric)
- Global search (corpus-wide summaries)
- Community-based insights

## Technology Stack

- **Backend**: Python, FastAPI, Microsoft Agent Framework
- **Database**: PostgreSQL 16 with pgvector + Apache AGE
- **LLM**: Azure OpenAI (gpt-4o, text-embedding-3-small)
- **GraphRAG**: Microsoft GraphRAG for knowledge graphs
- **Frontend**: React + TypeScript

## Development

```bash
# Run agents directly
uv run python backend\agents\contract_agent.py
uv run python backend\agents\router_agent.py

# Test ingestion
uv run python data_ingestion\ingestion_pipeline.py

# Generate seed data
uv run python scripts\generate_seed_data.py
```

---

**Hybrid Intelligence**: Combines structured SQL precision with GraphRAG's cross-document reasoning for comprehensive contract analysis.
