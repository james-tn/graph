# Contract Intelligence Platform - Design Document

## 1. Executive Summary
The Contract Intelligence Platform (CIP) is an enterprise-grade solution designed to ingest, analyze, and query complex legal portfolios. It leverages a **Hybrid Architecture** combining **Microsoft GraphRAG** (for holistic, thematic understanding) and **PostgreSQL** (for structural graph and vector analytics). The system uses **Agentic AI** to orchestrate complex reasoning tasks, enabling users to ask deep questions about risks, obligations, and portfolio trends.

## 2. System Architecture

### 2.1 High-Level Components
*   **Ingestion Service:** Background job runner for PDF processing.
*   **Knowledge Engine:**
    *   **GraphRAG:** Entity/Relationship extraction & Community Summarization.
    *   **PostgreSQL (Azure Database):** Unified store for Relational (Metadata), Graph (Apache AGE), and Vector (`pgvector`) data.
*   **Agentic Layer:** Python-based agent framework for orchestration.
*   **Frontend:** React-based "Contract Workspace" and "Intelligence Chat".

### 2.2 Data Flow
1.  **Upload:** User uploads PDF/Docx.
2.  **Vision Extraction:** `Ingestion Service` converts PDF -> Images -> Markdown using **GPT-5.1 Vision**.
3.  **Indexing:**
    *   **GraphRAG:** Extracts Entities/Relationships based on the *Rich Schema*.
    *   **Claim Extraction:** Extracts specific *Obligations* and *Rights*.
4.  **Sync:** Post-processing script loads GraphRAG artifacts (Parquet) into PostgreSQL (Graph + Vector).
5.  **Query:** Agent receives user query -> Selects Tool (SQL, GraphRAG, Vector) -> Synthesizes answer.

---

## 3. Ingestion Pipeline (Vision-Based)

To ensure high-fidelity extraction of tables, layout, and signatures, we utilize a Vision-First approach.

### 3.1 Workflow
1.  **Job Queue:** Uploads are pushed to a queue (e.g., Azure Queue Storage / BullMQ).
2.  **Conversion:**
    *   Convert PDF pages to high-res PNG images.
3.  **Vision Extraction (GPT-5.1):**
    *   **Prompt:** "Transcribe this contract page into Markdown. Preserve table structures, headers, and formatting. Identify signatures and handwritten notes."
    *   **Output:** Clean Markdown text.
4.  **Chunking:** Markdown is chunked by *Section* or *Clause* (smart chunking) rather than arbitrary token counts.

### 3.2 Failure & Retry
*   **State Tracking:** `ingestion_jobs` table tracks status (`pending`, `processing`, `failed`, `completed`).
*   **Retry Logic:** Exponential backoff for API failures.
*   **Dead Letter:** Failed jobs after N retries are flagged for manual review.

---

## 4. Rich Data Schema (Entities & Relationships)

To answer "Deep Questions," we move beyond simple "Party/Contract" entities.

### 4.1 Entities
| Entity Type | Description | Attributes (Examples) |
| :--- | :--- | :--- |
| `Contract` | The legal agreement itself. | `Type`, `EffectiveDate`, `ExpirationDate`, `Status`, `GoverningLaw` |
| `Party` | Organization or Person. | `Name`, `Role` (Vendor/Customer), `Jurisdiction` |
| `Clause` | Specific section of text. | `Type` (Indemnity, SLA), `RiskLevel`, `IsStandard` |
| `Obligation` | A mandatory action. | `ResponsibleParty`, `Beneficiary`, `DueDate`, `Penalty` |
| `Right` | A permissive action. | `Holder`, `Condition`, `Expiration` |
| `Term` | Defined term. | `Name`, `DefinitionText` |
| `Condition` | A trigger for an obligation. | `Description`, `TriggerEvent` |
| `Jurisdiction` | Legal domain. | `Region`, `Country`, `State` |
| `MonetaryValue` | Extracted financial amount. | `Amount`, `Currency`, `Type` (Fee, Cap, Penalty) |

### 4.2 Relationships
| Relationship | Source | Target | Description |
| :--- | :--- | :--- | :--- |
| `IS_PARTY_TO` | `Party` | `Contract` | Defines participation. |
| `CONTAINS_CLAUSE` | `Contract` | `Clause` | Structural hierarchy. |
| `IMPOSES_OBLIGATION` | `Clause` | `Obligation` | Semantic link. |
| `GRANTS_RIGHT` | `Clause` | `Right` | Semantic link. |
| `DEFINES_TERM` | `Clause` | `Term` | Definitions. |
| `CONDITIONAL_ON` | `Obligation` | `Condition` | Logic flow ("If X then Y"). |
| `AMENDS` | `Contract` | `Contract` | Version history. |
| `LOCATED_IN` | `Party` | `Jurisdiction` | Geographic risk. |
| `HAS_VALUE` | `Contract` | `MonetaryValue` | Financial link. |

---

## 5. Agentic Framework

We utilize a **Router-based Agent** architecture.

### 5.1 Core Agent
*   **Role:** Orchestrator.
*   **Input:** Natural Language Query.
*   **Logic:** Analyzes intent -> Selects Tool -> Aggregates Results.

### 5.2 Tools
1.  **`PortfolioAnalyticsTool` (SQL):**
    *   *Use Case:* Aggregations, filtering, hard constraints.
    *   *Implementation:* Text-to-SQL generation against the Postgres Metadata tables.
    *   *Query:* "Total value of contracts expiring in Q3."
2.  **`ThematicInsightTool` (GraphRAG):**
    *   *Use Case:* Summarization, trend analysis, "vibe check".
    *   *Implementation:* GraphRAG `global_search`.
    *   *Query:* "Summarize our liability risks with IT vendors."
3.  **`SemanticSearchTool` (Vector):**
    *   *Use Case:* Finding similar clauses, specific language.
    *   *Implementation:* `pgvector` cosine similarity.
    *   *Query:* "Find clauses discussing 'Force Majeure' due to pandemics."
4.  **`StructuralGraphTool` (Cypher/AGE):**
    *   *Use Case:* Multi-hop traversal, hidden connections.
    *   *Implementation:* Cypher query on Apache AGE.
    *   *Query:* "Find vendors connected to Sanctioned Entity X."

### 5.3 Complementary Capability Matrix (GraphRAG + Postgres)
The new Postgres deep insight layer augments, rather than replaces, the existing GraphRAG system. The router agent evaluates user intent and dispatches to one or more tools based on the evidence needed.

| Intent Pattern | GraphRAG Strength | Postgres Deep Insight Strength | Routing Guidance |
| --- | --- | --- | --- |
| Narrative / theme / trend questions ("What are the biggest risks?"), weakly structured | Community summaries preserve discourse context across the corpus | Structured store can still supply supporting clauses for citations | Route to **GraphRAG** for primary answer, then enrich citations from Postgres if needed |
| Portfolio aggregates, metrics, filters ("Count contracts expiring in 90 days") | Not optimized for precise numeric filters | SQL + analytics schema excel here | Route to **PortfolioAnalyticsTool** (Postgres) |
| Cross-contract relationship reasoning ("Which vendors lack DPAs governing EU data?") | GraphRAG relationships capture semantic neighborhoods | Graph edges w/ clause-level evidence ensure precise filtering | Prefer **StructuralGraphTool**. Use GraphRAG only if question is fuzzy or requires community context |
| Clause similarity / precedent search | GraphRAG embeddings available but not indexed for low-latency retrieval | `pgvector` indexes tuned for clause embeddings | Route to **SemanticSearchTool** |
| Keyword / phrase matches, numeric thresholds | Limited support | Full-text and trigram indexes deliver exact hits | Route to **KeywordSearchTool** |
| Executive summary with storytelling | Designed for holistic narrative | Can supply factual tables but not prose context | Route to **GraphRAG** (optionally cite Postgres rows) |

### 5.4 Router Decision Flow
- **Step 1 – Intent Classification:** A lightweight classifier looks for cues: metrics/counts, graph terms ("which", "connected to"), semantic similarity ("similar to", "like"), keywords (quoted text), or open-ended narrative prompts.
- **Step 2 – Tool Selection:**
  1. Numeric filters, aggregations → `PortfolioAnalyticsTool` (Postgres SQL).
  2. Multi-hop relationships or compliance logic → `StructuralGraphTool` (Postgres graph edges / AGE).
  3. Semantic clause hunt → `SemanticSearchTool` (Postgres).
  4. Exact phrase search → `KeywordSearchTool` (Postgres).
  5. Strategic themes / trend summaries → `ThematicInsightTool` (GraphRAG) with optional follow-up SQL fetch for citations.
- **Step 3 – Evidence Fusion:** Regardless of the primary tool, the router can call secondary tools to fetch clause-level citations (e.g., GraphRAG narrative + Postgres clause IDs) before composing the final answer.
- **Step 4 – Observability:** Each routing decision logs the chosen tool(s), rationale, and latency so product teams can tune the classifier over time.

---

## 6. Synthetic Data Utility

To seed the system for testing, we will build a `DataGenerator` utility.

### 6.1 Functionality
*   **Templates:** Uses a set of base templates (MSA, NDA, SOW).
*   **Variation:** Uses OpenAI to inject variations:
    *   *Parties:* Randomly generated names/addresses.
    *   *Clauses:* Standard vs. High Risk (e.g., "Uncapped Liability").
    *   *Dates:* Randomized within a range.
*   **Output:** Generates PDF files and a "Ground Truth" JSON for validation.

### 6.2 Prompt Strategy
"Generate a Master Services Agreement between 'Acme Corp' and 'Beta Ltd'. Include a 'Limitation of Liability' clause that is **unusually high** (3x fees). Set the Governing Law to 'California'."

---

## 7. UI/UX Concepts

### 7.1 Contract Insight Workspace
*   **Dashboard:** High-level metrics (Active Contracts, Risk Heatmap).
*   **Community Map:** Visual cluster map of vendors/contracts.

### 7.2 Intelligence Chat
*   **Split Screen:** Chat on left, Document Viewer on right.
*   **Citations:** Clicking a citation in the chat scrolls the Document Viewer to the exact clause (using the Markdown/Vision mapping).

---

## 8. Deep Insight Layer (PostgreSQL Graph + Vector)

### 8.1 Goals & Scope
- **Mission:** Operationalize the GraphRAG ontology on Azure Database for PostgreSQL Flexible Server so the platform can answer portfolio-level questions with relational, graph, vector, and keyword evidence.
- **Primary Capabilities:**
    1. Structured SQL analytics on normalized contract metadata.
    2. Graph traversal (Apache AGE if available, otherwise relational edge tables) for multi-hop reasoning.
    3. Semantic clause retrieval via `pgvector` embeddings.
    4. Keyword and exact phrase search via `tsvector` + GIN indexes.
- **Agent Exposure:** All capabilities must be surfaced as tools that the router agent can invoke with citations.

### 8.2 Ontology Implementation
- **Entity Tables:** Implement the extended set specified in the requirements (Contract, Party, Clause, Obligation, Right, TermDefinition, Condition, Jurisdiction, MonetaryValue, Risk, DataCategory, ProductOrSystem). Each table carries tenant scoping (`tenant_id`), auditing columns (`created_at`, `updated_at`), and soft-delete flags for future use.
- **Representative Columns:**
    - `contracts`: lifecycle metadata (`contract_type`, `term_type`, `status`, `risk_score_overall`, `source_markdown_location`).
    - `clauses`: structure + analytics (`section_label`, `clause_type`, `risk_level`, `is_standard`, `text`, `embedding vector(1536)`, `full_text_vector tsvector`).
    - `obligations` / `rights`: normalized descriptions, party roles, timing, penalties, `is_high_impact` flags.
    - `monetary_values`: `amount`, `currency`, `value_type`, `context`, optional `multiple_of_fees`.
    - `risks`: `risk_type`, `risk_level`, `rationale`, `detected_by`, `is_confirmed`.
- **Relationship Tables / Graph Edges:** Persist both FK constraints and explicit edge tables (or AGE edges) for `IS_PARTY_TO`, `CONTAINS_CLAUSE`, `IMPOSES_OBLIGATION`, `GRANTS_RIGHT`, `DEFINES_TERM`, `CONDITIONAL_ON`, `AMENDS`, `LOCATED_IN`, `GOVERNED_BY`, `HAS_VALUE`, `TAGGED_AS_RISK`, `RELATES_TO_DATA_CATEGORY`, and `RELATES_TO_PRODUCT`.
- **Extensibility:** Use lookup tables (`clause_types`, `risk_types`, `party_roles`) so new domain concepts can be added without schema rewrites.

### 8.3 Storage & Extension Strategy
- **Azure Database for PostgreSQL Flexible Server:**
    - Private VNet integration, zone redundant HA, customer-managed keys (CMK) ready.
    - Enable extensions: `pgvector`, `pg_trgm`, `hstore`, `citext`, and `azure_age` (or equivalent) after verifying support in the target region/SKU.
- **Indexing:**
    - `pgvector` columns use `ivfflat` (production) with `lists` tuned per corpus size; fall back to `hnsw` once supported.
    - Text-heavy columns include `tsvector` stored columns with GIN indexes (`USING gin(full_text_vector)`).
    - High-cardinality FK relationships get B-Tree indexes to accelerate joins.
- **Graph Representation:**
    - **Option A:** Apache AGE graph `CREATE GRAPH cip_graph` with node labels mirroring tables and edges carrying FK references.
    - **Option B:** Edge tables + `VIEW`s that surface Cypher-like traversals if AGE is unavailable. Helper functions encapsulate recursive queries.

### 8.4 Ingestion & Extraction Pipeline Enhancements
1. **Clause Segmentation:** Use existing Markdown chunker; guarantees `section_label` + `title` capture.
2. **Classification & Risk:** LLM prompts classify `clause_type`, `risk_level`, `is_standard`; results stored with raw JSON for auditing.
3. **Obligation / Right Extraction:** Targeted prompts per clause type produce structured rows plus any `Condition` definitions.
4. **Monetary Values:** Regex + LLM hybrid pipeline extracts `amount`, `currency`, `context`, `multiple_of_fees`.
5. **Risk Tagging:** Rule set + LLM evaluation populates `risks` table and `TAGGED_AS_RISK` edges.
6. **Embeddings:** Generate Azure OpenAI text-embedding-3-large vectors for clauses, obligations, and (optionally) rights; push into `pgvector` columns with nightly reindex jobs.
7. **Keyword Indexing:** `to_tsvector('english', clause_text)` persisted column maintained via trigger.
8. **Job Tracking:** `extraction_jobs` table stores status, retries, timestamps, and error payloads to support observability.

### 8.5 Agent Tooling Contracts
- **PortfolioAnalyticsTool (SQL):** Text-to-SQL service with schema registry + guardrails; enforces tenant filters and column allow-list. Returns structured JSON plus row-level citations (contract_id/clause_id).
- **StructuralGraphTool:** Wrapper over AGE/Cypher (or SQL recursion) that accepts validated templates for common traversals (e.g., vendor risk path). Provides multi-hop answers referencing node IDs.
- **SemanticSearchTool:** Combines embedding similarity + optional metadata filters. Returns top-N clauses with `similarity_score`, snippet, and contract metadata.
- **KeywordSearchTool:** Parameterized `tsquery` builder allowing phrase search + clause type filtering.
- **ThematicInsightTool:** Existing GraphRAG summarizer now references Postgres IDs so citations can bridge both stores.
- **Router Logic:** Intent classifier chooses tool combos, merges outputs, and ensures final answer lists `contract_id`, `clause_id`, `section_label`.

### 8.6 API Surface
- `GET /contracts/{id}`: metadata + top clauses + risk summary.
- `POST /clauses/search`: accepts `keyword_query`, `semantic_query`, filters (party, clause_type, risk) and returns paged results.
- `POST /insights/graph-query`: internal API executing curated Cypher/SQL graph templates.
- `POST /chat/query`: orchestrates agent call, returns `answer`, `citations`, `tool_invocations` for observability.
- All APIs enforce RBAC/tenant scoping and emit structured logs for replay.

### 8.7 Non-Functional Drivers
- **Performance:** 3–5 second target per agent answer; asynchronous ingestion sized for 1k contracts/day with autoscaled worker pool.
- **Scalability:** Partition tables by `tenant_id` (and optionally `effective_date`), leverage read replicas for analytics, and batch re-embedding jobs.
- **Security:** TLS enforced end-to-end, private endpoints, Azure AD auth, Key Vault-managed connection secrets, minimal RBAC roles.
- **Observability:** Centralized logging of tool calls (SQL, Cypher, vector) with execution time, row counts, error traces, plus metric dashboards per tool.
- **Data Quality:** Schema validation on LLM outputs, manual QA sampling workflows, audit logs for corrections, and `is_confirmed` flags on risky findings.

---

## 9. Multi-Agent Orchestration (Microsoft Agent Framework)

### 9.1 Rationale & Evaluation
The Microsoft Agent Framework already ships opinionated patterns for graph-based workflows, router agents, and specialized tool agents in both Python and .NET. Key capabilities we will leverage:
- **Graph Workflows:** Native support for DAG-style orchestration allows us to model Router → Tool Agent → Evidence Fuse nodes with streaming and retries.
- **Agent Specialization:** Each agent can carry its own instruction set, tool belt, and memory, which maps cleanly to our GraphRAG vs. Postgres dichotomy.
- **Observability & Checkpointing:** Built-in OpenTelemetry hooks plus workflow checkpoints let us log every tool invocation and replay problematic sessions.
- **Multi-language parity:** We can prototype in Python (aligning with the existing backend) while keeping the option to expose .NET agents for future integrations.

### 9.2 Target Agent Topology

```
User Question → RouterAgent → (Primary Tool Agent) → EvidenceFusionAgent → Answer
                                                        ↘ (Secondary Tool Agent)*
```

- **RouterAgent:** Lightweight LLM agent instructed via `router_agent.md`. It emits a JSON routing plan (primary + optional secondary tools) based on the guidelines in §5.3/5.4.
- **GraphRAG Agent:** Wraps the existing GraphRAG service (`ThematicInsightTool`). Provides narrative summaries, community context, and macro trends.
- **Postgres Insight Agent:** New specialized agent that can: (a) author SQL for analytics, (b) craft Cypher/edge SQL for graph traversals, (c) compose pgvector semantic search queries, and (d) run keyword / hybrid searches. Instructions captured in `backend/app/prompts/postgres_sql_agent.md`.
- **Evidence Fusion Agent:** Deterministic component that merges outputs, normalizes citations (contract_id/clause_id/section_label), and formats the final response for the frontend.

### 9.3 Agent Framework Implementation Plan
1. **Workflow Definition:** Use the Python Agent Framework workflow primitives to register nodes for Router, GraphRAG Tool, Postgres Tool, and Evidence Fusion. Router node inspects its own LLM response and schedules downstream nodes dynamically.
2. **Tool Clients:**
    - GraphRAG client already exists within the backend services; expose it as a callable tool for the GraphRAG agent.
    - Postgres Insight agent will call a Toolbelt consisting of `portfolio_sql_executor`, `graph_query_executor`, `semantic_search_executor`, and `keyword_search_executor`. Each tool talks to FastAPI endpoints that ultimately hit PostgreSQL.
3. **Hybrid Retrieval:** For semantic + keyword combined queries, the agent first runs pgvector similarity, then re-ranks/filters results using keyword tsquery to ensure precision. The instructions require the agent to explain when hybrid mode is needed (e.g., searching for "Data Breach" with concept drift).
4. **Prompt Grounding:** Router + Postgres prompts live in versioned files under `backend/app/prompts`. We load them into the agent framework at startup, keeping configuration declarative.
5. **Observability Hook:** Each workflow run emits structured logs containing router choice, SQL/graph/vector statements, latencies, and row counts, enabling future evaluation and optimizer loops.

### 9.4 Postgres Insight Agent Capabilities
- **SQL Analytics:** Generate safe, parameterized SQL for counts, sums, averages, percentile calculations, and filtering by clause/contract attributes. Must always include tenant filters and LIMITs.
- **Graph Traversal:** When the router flags relationship queries, compose Cypher (AGE) or recursive SQL templates such as party → contract → clause → risk. Respond with both the query plan and the rows needed for citations.
- **Semantic Vector Search:** Compute embeddings for the user text (via Azure OpenAI) and call `/api/search/semantic` with filters (clause_type, party, risk). Handles k-nearest-neighbor and optional metadata filtering.
- **Keyword / Hybrid Search:** Use `/api/search/keyword` for exact phrases. When both conceptual and literal matching are needed, run semantic search first, then refine via keyword filter inside Postgres (tsquery + vector similarity threshold) and merge results.
- **Result Packaging:** Always return structured JSON containing rows plus metadata describing which executor ran, similarity scores, ranking rationale, and ready-to-display citations.

### 9.5 Next Implementation Steps
1. Implement Agent Framework workflow scaffolding (Python) that instantiates Router + specialized agents using the prompts documented above.
2. Build FastAPI endpoints for SQL, graph, vector, and keyword executors so the Postgres agent has deterministic tools.
3. Add automated evaluation harnesses to compare router decisions vs. ground-truth routing using synthetic queries.
4. Integrate observability by wiring workflow telemetry into the existing logging pipeline.
