# Quick Start Guide - Contract Intelligence Platform

## Step 1: Install Dependencies

Using `uv` for fast package installation:

```bash
cd c:\testing\graph\contract_intelligence
uv sync
```

## Step 2: Azure Authentication

Ensure you're authenticated with Azure:

```bash
az login
```

This will allow the script to use `DefaultAzureCredential` to access Azure OpenAI.

## Step 3: Configure Environment

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and set:
```env
AZURE_OPENAI_ENDPOINT=https://eastus2oai.openai.azure.com/openai/v1/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1
```

## Step 4: Generate Seed Data

Run the seed data generator to create 45 realistic contracts:

```bash
uv run python scripts/generate_seed_data.py
```

This will:
- Generate 45 diverse contracts (MSAs, SOWs, NDAs, etc.)
- Each contract will be 6-7 pages (3500-5000 words)
- Vary risk levels (Low, Medium, High)
- Save as Markdown files in `data/input/`

**Expected Runtime:** ~15-25 minutes (depending on API rate limits)

## Step 5: Run GraphRAG Indexing

Once the contracts are generated, run the GraphRAG indexing pipeline:

```bash
uv run python -m graphrag.index --root . --config graphrag_config/settings.yaml
```

This will:
- Extract entities (Contracts, Parties, Clauses, Obligations, Risks)
- Build relationships between entities
- Create hierarchical communities
- Generate community summaries
- Output artifacts to `data/output/`

**Expected Runtime:** ~30-60 minutes for 45 contracts

## Step 6: Verify Output

Check the generated artifacts:

```bash
dir data\output\artifacts
```

You should see files like:
- `create_final_nodes.parquet`
- `create_final_entities.parquet`
- `create_final_relationships.parquet`
- `create_final_communities.parquet`
- `create_final_community_reports.parquet`

## Next Steps

After indexing completes:
1. Build the PostgreSQL sync script (to load GraphRAG output into Postgres)
2. Implement the Agent API
3. Build the React frontend

## Troubleshooting

### Authentication Issues
If you get authentication errors:
```bash
az account show  # Verify you're logged in
az account list  # Check available subscriptions
```

### Rate Limiting
If you hit rate limits during seed generation, the script will automatically batch requests with delays. You can reduce `batch_size` in the script if needed.

### Memory Issues
If GraphRAG indexing runs out of memory, reduce `parallelization.num_threads` in `settings.yaml`.
