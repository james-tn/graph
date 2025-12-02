# Contract Intelligence Platform

This project implements a hybrid Contract Intelligence Platform using Microsoft GraphRAG and PostgreSQL (Graph + Vector).

## Business Context & Vision

### The Challenge
Modern enterprises manage thousands of contracts—with vendors, customers, and partners—that contain critical operational data, financial obligations, and hidden risks. Traditional Contract Lifecycle Management (CLM) tools are often static repositories. They struggle to answer complex, cross-portfolio questions like *"What is our aggregate liability exposure across all IT vendors?"* or *"Which contracts conflict with our new 2025 Data Privacy Policy?"*

### The Solution Landscape
To solve this, two primary AI architectures have emerged:
1.  **GraphRAG (Retrieval-Augmented Generation):** Excels at **holistic understanding**. It builds a knowledge graph to summarize themes, detect "drift" in terms, and answer broad questions ("What are the standard payment terms?").
2.  **Graph Databases + Vector Search:** Excels at **structural precision**. It allows for multi-hop traversal ("Find the ultimate owner of this vendor") and semantic search ("Find clauses similar to this text").

### Our Hybrid Approach
This platform implements a **Hybrid Architecture** that combines the best of both worlds:
*   **Microsoft GraphRAG** serves as the "Ingestion & Reasoning Engine," extracting entities, relationships, and thematic communities from unstructured text.
*   **PostgreSQL (Graph + Vector)** serves as the "Analytical Store," enabling precise SQL filtering, recursive graph traversal (via Apache AGE), and semantic vector search (via `pgvector`).

### Vision & Capabilities
This solution delivers an **Agentic AI** experience where users can ask:
*   **Portfolio Visibility:** "Show all contracts expiring in Q4 with a value > $50k." (SQL/Structured)
*   **Deep Risk Analysis:** "Identify vendors with uncapped liability who are also in high-risk jurisdictions." (Graph Traversal)
*   **Thematic Insight:** "Summarize how our indemnification clauses have evolved over the last 3 years." (GraphRAG Summarization)
*   **Semantic Discovery:** "Find every contract that contains language similar to this specific Force Majeure clause." (Vector Search)

### Future Expansion
While built for Contract Intelligence, this architecture is industry-agnostic and can expand to:
*   **M&A Due Diligence:** Rapidly analyzing a target company's legal risks.
*   **Supply Chain Intelligence:** Mapping multi-tier supplier relationships and dependencies.
*   **Regulatory Compliance:** Automatically auditing internal policies against external regulations (e.g., GDPR, DORA).

## Project Structure

- `backend/`: FastAPI backend service.
- `frontend/`: React frontend (placeholder).
- `data/`: Data storage.
    - `input/`: Place your `.md` or `.txt` contract files here.
    - `output/`: GraphRAG artifacts will be generated here.
- `graphrag_config/`: Configuration and prompts for GraphRAG.
- `scripts/`: Utility scripts (seeding, setup).

## Setup

1.  **Environment Variables:**
    Create a `.env` file in the root or backend directory with the following:
    ```env
    AZURE_OPENAI_API_KEY=your_azure_openai_key
    AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
    AZURE_OPENAI_API_VERSION=2024-02-15-preview
    AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
    EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small
    POSTGRES_CONNECTION_STRING=postgresql://user:password@host:port/dbname
    ```

2.  **Install Dependencies:**
    ```bash
    uv sync
    ```

3.  **Run GraphRAG Indexing:**
    ```bash
    uv run python -m graphrag.index --root . --config graphrag_config/settings.yaml
    ```

4.  **Run Backend:**
    ```bash
    cd backend
    uv run uvicorn app.main:app --reload
    ```

## Infrastructure Provisioning with azd

The repo ships with `azure.yaml` and Bicep templates so you can provision the PostgreSQL Flexible Server (v16 with pgvector + AGE) via the Azure Developer CLI.

1. Install azd and authenticate:
    ```bash
    azd auth login
    ```
2. Create/select an environment:
    ```bash
    azd env new contract-intel-dev
    ```
3. Populate the required secrets:
    ```bash
    azd env set POSTGRES_ADMIN_PASSWORD <secure-password>
    ```
4. Provision the infrastructure:
    ```bash
    azd up
    ```

Under the hood azd executes `infra/main.bicep`, which first creates the VNet + delegated subnet + private DNS zone (matching the naming conventions in `infra/networking.bicep`) and then provisions Azure Database for PostgreSQL Flexible Server with the `pgvector`, `pg_trgm`, `hstore`, `citext`, and `age` extensions enabled.

## Design

See `DESIGN.md` for the detailed architectural design.
