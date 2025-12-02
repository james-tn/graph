# Contract Intelligence - Hybrid Graph Search System

## 🎯 Overview

A next-generation contract analysis platform combining **PostgreSQL + Apache AGE** with **Microsoft GraphRAG** for hybrid graph search capabilities. The system intelligently routes queries to the optimal backend based on query characteristics.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  (Hybrid Search UI with Strategy Selection)                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│                  (Router Agent)                             │
└─────────────────────────────────────────────────────────────┘
                     │              │
        ┌────────────┴───────┬──────┴──────────┐
        ▼                    ▼                  ▼
┌───────────────┐    ┌──────────────┐   ┌──────────────┐
│  PostgreSQL   │    │   GraphRAG   │   │    Hybrid    │
│     Agent     │    │    Agent     │   │   (Both)     │
└───────────────┘    └──────────────┘   └──────────────┘
        │                    │
        ▼                    ▼
┌───────────────┐    ┌──────────────┐
│  PostgreSQL   │    │   GraphRAG   │
│  + AGE Graph  │    │ Knowledge    │
│   Database    │    │    Graph     │
└───────────────┘    └──────────────┘
```

## 🚀 Features

### Dual Ingestion Pipeline
- **PostgreSQL Ingestion**: Structured data with entities, relationships, clauses
- **GraphRAG Indexing**: Knowledge graph with community detection
- **Parallel Processing**: Ingests 5 contracts simultaneously

### Intelligent Query Routing
- **Auto Mode**: AI-powered routing based on query characteristics
- **PostgreSQL Mode**: For precise lookups, SQL queries, graph traversal
- **GraphRAG Mode**: For pattern discovery, cross-document analysis
- **Hybrid Mode**: Combines results from both sources

### PostgreSQL Capabilities
- SQL analytics and aggregations
- Vector similarity search (clause embeddings)
- Full-text keyword search
- Apache AGE graph traversal (multi-hop queries)
- 9 specialized tools for contract queries

### GraphRAG Capabilities
- Entity extraction with community detection
- Local search (entity-centric with context)
- Global search (high-level corpus-wide summaries)
- Cross-document pattern analysis

## 📁 Project Structure

```
contract_intelligence/
├── backend/
│   ├── ingestion.py           # Dual pipeline (PostgreSQL + GraphRAG)
│   ├── build_graph.py          # Apache AGE graph creation
│   ├── schema.sql              # PostgreSQL schema
│   ├── agents/
│   │   ├── contract_agent.py   # PostgreSQL agent (9 tools)
│   │   ├── graphrag_agent.py   # GraphRAG query agent
│   │   └── router_agent.py     # Intelligent routing
│   └── app/
│       └── main.py             # FastAPI application
├── frontend/
│   └── src/
│       ├── App.tsx             # Main application
│       ├── api.ts              # API client
│       └── components/
│           ├── HybridQuerySection.tsx    # Search UI
│           └── HybridResultSection.tsx   # Results display
├── data/
│   ├── input/                  # Contract markdown files
│   └── output/                 # GraphRAG output
├── graphrag_config/
│   └── settings.yaml           # GraphRAG configuration
└── output/
    └── lancedb/                # Vector embeddings
```

## 🔧 Setup

### 1. Environment Variables

Create `.env` file:

```bash
# PostgreSQL Configuration
POSTGRES_HOST=your-postgres-server.postgres.database.azure.com
POSTGRES_DATABASE=cipgraph
POSTGRES_USER=pgadmin
POSTGRES_ADMIN_PASSWORD=YourPassword123!

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1
EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r backend/requirements.txt
pip install graphrag
pip install agent-framework

# Frontend dependencies
cd frontend
npm install
```

### 3. Run Dual Ingestion

```bash
# Ingests ALL contracts to PostgreSQL + GraphRAG
python backend/ingestion.py
```

This will:
1. ✅ Process all 30 contracts into PostgreSQL (5 parallel workers)
2. ✅ Extract entities, clauses, obligations, rights
3. ✅ Generate embeddings for semantic search
4. ✅ Run GraphRAG indexing for knowledge graph

### 4. Start Backend

```bash
# Terminal 1: FastAPI Backend
cd backend/app
python main.py
```

### 5. Start Frontend

```bash
# Terminal 2: React Frontend
cd frontend
npm run dev
```

## 🎮 Usage

### Web Interface

1. **Open**: http://localhost:5173
2. **Select Strategy**: Auto / PostgreSQL / GraphRAG / Hybrid
3. **Enter Query**: Type your question
4. **View Results**: See routing decision + unified response

### API Endpoints

```bash
# Hybrid Query
POST /api/query
{
  "query": "What are liability caps across all contracts?",
  "strategy": "auto"  # or "postgres", "graphrag", "hybrid"
}

# Analyze Query (no execution)
POST /api/analyze
{
  "query": "Compare termination conditions"
}

# Get Statistics
GET /api/stats

# Health Check
GET /health
```

## 📊 Query Examples

### PostgreSQL-Routed Queries
```
✅ "Show me all contracts for Acme Corp"
✅ "What obligations does Vanguard Solutions have?"
✅ "Find clauses about liability limitations"
✅ "List high-risk clauses in contract_000"
✅ "What are the payment terms in our contracts?"
```

### GraphRAG-Routed Queries
```
🧠 "What are common risk patterns across all contracts?"
🧠 "Compare termination conditions between vendors"
🧠 "Summarize all unusual terms found"
🧠 "What are industry-standard SLA terms?"
🧠 "Identify cross-contract themes and trends"
```

### Hybrid Queries
```
🔀 "Which contracts have non-standard liability caps?"
🔀 "Show relationships between parties and obligations"
🔀 "Find contracts with unusual renewal terms"
```

## 🔍 Routing Decision Logic

The **Router Agent** analyzes queries using:

1. **Pattern Matching**: Keywords indicating structured vs. graph queries
2. **LLM Analysis**: GPT-4 determines optimal routing strategy
3. **Confidence Scores**: PostgreSQL score vs. GraphRAG score

### Routing Criteria

| Query Type | PostgreSQL Score | GraphRAG Score | Strategy |
|------------|------------------|----------------|----------|
| "contract X" | High | Low | PostgreSQL |
| "all contracts" | Low | High | GraphRAG |
| "compare X and Y" | Medium | High | GraphRAG |
| "party obligations" | High | Low | PostgreSQL |
| "common patterns" | Low | High | GraphRAG |
| "unusual terms" | Medium | Medium | Hybrid |

## 📈 Performance

- **PostgreSQL**: ~2-5s per query (includes LLM tool calls)
- **GraphRAG Local Search**: ~10-15s (entity extraction + context building)
- **GraphRAG Global Search**: ~30-60s (map-reduce over communities)
- **Hybrid**: Parallel execution (max of both)

## 🎨 UI Features

- **Strategy Selector**: Choose routing approach
- **Sample Queries**: Pre-defined examples with routing hints
- **Routing Explanation**: Shows why query was routed to specific backend
- **Source Attribution**: Clear indication of PostgreSQL vs. GraphRAG
- **Detailed Results**: Expandable raw responses from both sources
- **Markdown Support**: Rich formatting for responses

## 🔐 Security

- ✅ Environment variable configuration (no hardcoded secrets)
- ✅ SSL connections to PostgreSQL
- ✅ Azure AD authentication for Agent Framework
- ✅ CORS configured for frontend-backend communication

## 📝 Data Schema

### PostgreSQL Tables
- `contracts`: Contract metadata
- `parties`: Organizations involved
- `clauses`: Individual contract sections with embeddings
- `obligations`: Required actions
- `rights`: Granted permissions
- `monetary_values`: Financial terms
- `risks`: Identified risk items
- `term_definitions`: Defined terms

### GraphRAG Output
- `create_final_entities.parquet`: Extracted entities
- `create_final_relationships.parquet`: Entity relationships
- `create_final_communities.parquet`: Community detection
- `create_final_community_reports.parquet`: Community summaries
- `create_final_text_units.parquet`: Text chunks with metadata

## 🚧 Development

### Adding New PostgreSQL Tools

Edit `backend/agents/contract_agent.py`:

```python
@tool
def new_query_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return result
```

### Modifying Router Logic

Edit `backend/agents/router_agent.py`:

```python
# Add patterns
POSTGRES_PATTERNS = [...]
GRAPHRAG_PATTERNS = [...]

# Modify analyze_query() for custom logic
```

## 📚 References

- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [Apache AGE](https://age.apache.org/)
- [Agent Framework](https://github.com/microsoft/agent-framework)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)

## 🎯 Next Steps

1. ✅ **Implemented**: Dual ingestion pipeline
2. ✅ **Implemented**: Intelligent router agent
3. ✅ **Implemented**: Hybrid search UI
4. 🔄 **TODO**: Background ingestion jobs
5. 🔄 **TODO**: Query history and favorites
6. 🔄 **TODO**: Advanced filtering and facets
7. 🔄 **TODO**: Export results to PDF/Excel
8. 🔄 **TODO**: Real-time collaboration features

## 💡 Tips

- Use **Auto mode** for best results (AI-powered routing)
- Use **PostgreSQL** for specific contract lookups
- Use **GraphRAG** for cross-contract analysis
- Use **Hybrid** when you want both perspectives

---

**Built with ❤️ using Microsoft GraphRAG and Agent Framework**
