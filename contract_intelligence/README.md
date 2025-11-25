# Contract Intelligence Platform

Enterprise-grade contract intelligence system using **Azure OpenAI**, **PostgreSQL with pgvector and Apache AGE**, and **Microsoft Agent Framework**.

## Features

- 🤖 **LLM-Powered Extraction** - Comprehensive entity and relationship extraction from contracts
- 📊 **Graph Database** - Apache AGE for multi-hop relationship queries
- 🔍 **Semantic Search** - pgvector with Azure OpenAI embeddings (1536d)
- 🎯 **AI Agent** - Natural language queries with automatic tool selection
- ⚖️ **Risk Analysis** - Automated clause classification and risk detection

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Contract Intelligence                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Ingestion   │  │    Graph     │  │   AI Agent   │     │
│  │   Pipeline   │→ │   Builder    │→ │  w/ Tools    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                   │            │
│         └──────────────────┴───────────────────┘            │
│                            ↓                                │
│              ┌──────────────────────────┐                   │
│              │   PostgreSQL Database    │                   │
│              │  • pgvector (embeddings) │                   │
│              │  • Apache AGE (graph)    │                   │
│              │  • Full-text search      │                   │
│              └──────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

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

### Run the Pipeline

```bash
start.bat
```

This will:
1. **Ingest contracts** with LLM extraction (contracts, parties, clauses, obligations, rights, terms, monetary values)
2. **Build graph** in Apache AGE (nodes and relationships)
3. **Run AI agent** with SQL, vector search, and graph traversal queries

## Project Structure

```
contract_intelligence/
├── scripts/
│   ├── ingestion/
│   │   └── ingest.py              # LLM-based contract ingestion
│   ├── graph/
│   │   └── build_graph.py         # Apache AGE graph builder
│   ├── agent/
│   │   └── run_agent.py           # AI agent with graph tools
│   └── tests/                     # Test and validation scripts
├── backend/
│   ├── schema.sql                 # PostgreSQL schema
│   └── requirements.txt           # Python dependencies
├── data/
│   ├── input/                     # Contract files (markdown)
│   └── output/                    # Processing results
├── infra/                         # Azure infrastructure (Bicep)
├── README.md                      # This file
├── README_TECHNICAL.md            # Technical deep-dive
├── DESIGN.md                      # Architecture design
└── start.bat                      # Main startup script
```

## Extracted Entities

The system extracts rich structured data from contracts:

- **Contracts** - Metadata, dates, governing law
- **Parties** - Legal entities with roles and jurisdictions
- **Clauses** - Sections with classification and risk levels
- **Obligations** - Mandatory actions with parties and penalties
- **Rights** - Permissive actions with holders
- **Terms** - Defined terminology
- **Monetary Values** - Amounts with context
- **Conditions** - Trigger events

## Graph Relationships

Apache AGE enables multi-hop queries via relationships:

- `IS_PARTY_TO` - Party ↔ Contract
- `CONTAINS_CLAUSE` - Contract ↔ Clause
- `IMPOSES_OBLIGATION` - Clause ↔ Obligation
- `RESPONSIBLE_FOR` - Party ↔ Obligation
- `GRANTS_RIGHT` - Clause ↔ Right
- `HOLDS_RIGHT` - Party ↔ Right
- `DEFINES_TERM` - Contract ↔ Term

## Example Queries

### Simple Analytics
```
"What contracts do we have?"
"Show contracts involving Acme Corp"
"Find high-risk clauses"
```

### Semantic Search
```
"Find clauses about data protection"
"Show liability limitation clauses"
```

### Graph Traversal (Multi-Hop)
```
"What obligations does Acme Corp have?"
"What rights does the vendor hold?"
"Analyze all relationships for contract_000"
```

## Agent Tools

The AI agent has 9 specialized tools:

### SQL-Based Tools
1. `get_contract_statistics()` - Portfolio analytics
2. `search_contracts_by_party()` - Party filtering
3. `search_clauses_semantic()` - Vector similarity search
4. `search_clauses_keyword()` - Full-text keyword search
5. `find_high_risk_clauses()` - Risk analysis
6. `list_contract_clauses()` - Contract navigation

### Graph Tools
7. `find_party_obligations()` - Multi-hop obligation discovery
8. `find_party_rights()` - Multi-hop right discovery
9. `analyze_contract_relationships()` - Complete relationship network

## Technology Stack

- **LLM**: Azure OpenAI (gpt-4.1 for extraction, text-embedding-3-small for embeddings)
- **Database**: PostgreSQL 16 Flexible Server
- **Extensions**: pgvector (vector), Apache AGE (graph), pg_trgm (full-text)
- **Agent Framework**: Microsoft Agent Framework (Python)
- **Infrastructure**: Azure (Bicep templates)

## Documentation

- **[README_TECHNICAL.md](README_TECHNICAL.md)** - Technical implementation details, LLM prompts, performance characteristics
- **[DESIGN.md](DESIGN.md)** - Architecture design, ontology, data model
- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step setup guide

## Key Advantages

### vs Pure SQL
✅ Multi-hop relationship queries  
✅ Complex network analysis  
✅ Path finding and traversal  

### vs Pure Vector Search
✅ Structured relationships  
✅ Exact entity linkage  
✅ Explainable connections  

### vs Keyword Matching
✅ Semantic understanding  
✅ Context preservation  
✅ Rich entity extraction  

## Development

### Running Individual Components

```bash
# Ingestion only
uv run scripts\ingestion\ingest.py

# Graph building only
uv run scripts\graph\build_graph.py

# Agent only
uv run scripts\agent\run_agent.py
```

### Testing

```bash
# Validate PostgreSQL extensions
uv run scripts\tests\test_postgres_graph_vector.py

# Test deprecated ingestion (for comparison)
uv run scripts\tests\deprecated_ingest.py
```

## Support

For questions or issues:
- Review [README_TECHNICAL.md](README_TECHNICAL.md) for implementation details
- Check [DESIGN.md](DESIGN.md) for architecture
- Examine `backend/schema.sql` for database structure

---

**Built with ❤️ using Azure OpenAI, PostgreSQL, and Microsoft Agent Framework**
