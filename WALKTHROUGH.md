# 🧭 Building a Structured Agentic Graph RAG System

> **A conceptual walkthrough for architects and engineers** — from "why graphs?" to a production-ready dual-engine intelligence platform

This document walks through the **key concepts, architecture decisions, and implementation patterns** behind building a rich, structured, agentic Graph RAG system. It's designed as a presentation companion — read it before diving into any specific implementation.

---

## 📖 Table of Contents

1. [Why Plain RAG Falls Short](#1-why-plain-rag-falls-short)
2. [The Graph RAG Thesis](#2-the-graph-rag-thesis)
3. [Choosing Your Graph Strategy](#3-choosing-your-graph-strategy)
4. [Architecture: The Dual-Engine Pattern](#4-architecture-the-dual-engine-pattern)
5. [Data Ingestion: From Documents to Graphs](#5-data-ingestion-from-documents-to-graphs)
6. [The Structured Knowledge Graph](#6-the-structured-knowledge-graph)
7. [The Statistical Knowledge Graph (GraphRAG)](#7-the-statistical-knowledge-graph-graphrag)
8. [Agentic Query Routing](#8-agentic-query-routing)
9. [Vector Search in a Graph World](#9-vector-search-in-a-graph-world)
10. [Key Challenges & Lessons Learned](#10-key-challenges--lessons-learned)
11. [Production Considerations](#11-production-considerations)

---

## 1. Why Plain RAG Falls Short

Traditional Retrieval-Augmented Generation (RAG) works well for simple Q&A over documents. But it breaks down when your domain has **structure, relationships, and cross-document dependencies**.

```mermaid
graph LR
    subgraph "Traditional RAG"
        Q1["Question"] --> Embed1["Embed Query"]
        Embed1 --> Search1["Vector Search"]
        Search1 --> Chunks["Top-K Chunks"]
        Chunks --> LLM1["LLM"]
        LLM1 --> A1["Answer"]
    end

    style Q1 fill:#ffebee,stroke:#c62828
    style A1 fill:#e8f5e9,stroke:#2e7d32
    style Chunks fill:#fff3e0,stroke:#ef6c00
```

### What traditional RAG misses

| Limitation | Example |
|---|---|
| **No relationship awareness** | "Which vendors share subcontractors?" — requires traversing connections |
| **No hierarchy understanding** | An Amendment modifies a SOW which is under an MSA — flat chunks lose this |
| **No aggregation** | "Total spend across all active contracts" — can't SUM over chunks |
| **No cross-document patterns** | "Common themes in high-risk clauses" — requires corpus-wide analysis |
| **Hallucination on structure** | LLM invents data when chunks lack precise numbers or dates |

### The core insight

> **Documents contain both _content_ and _structure_. Traditional RAG captures content but discards structure. Graph RAG preserves both.**

```mermaid
graph TB
    Doc["📄 Source Document"]
    
    Doc --> FlatRAG["Flat RAG"]
    Doc --> GraphRAG["Graph RAG"]
    
    FlatRAG --> Chunks2["Text Chunks + Embeddings"]
    Chunks2 --> Loss["❌ Relationships Lost<br/>❌ Hierarchy Lost<br/>❌ Entities Duplicated"]
    
    GraphRAG --> Structured["Entities + Relationships"]
    GraphRAG --> Embeddings["Text Chunks + Embeddings"]
    Structured --> Gain["✅ Traversable Graph<br/>✅ Hierarchy Preserved<br/>✅ Entities Resolved"]
    Embeddings --> Gain
    
    style Loss fill:#ffebee,stroke:#c62828
    style Gain fill:#e8f5e9,stroke:#2e7d32
    style Doc fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
```

---

## 2. The Graph RAG Thesis

Graph RAG combines the **semantic power of embeddings** with the **structural power of graphs**. There are two complementary approaches:

```mermaid
graph TB
    subgraph "Approach 1: Structured Knowledge Graph"
        direction TB
        SKG1["Domain Schema Design"]
        SKG2["LLM Entity Extraction"]
        SKG3["Graph Database<br/>(Neo4j, AGE, Neptune)"]
        SKG4["Cypher/Gremlin Queries"]
        SKG1 --> SKG2 --> SKG3 --> SKG4
    end
    
    subgraph "Approach 2: Statistical Knowledge Graph"
        direction TB
        EKG1["LLM Entity + Relationship Extraction"]
        EKG2["Community Detection Algorithm"]
        EKG3["Community Summarization"]
        EKG4["Map-Reduce over Summaries"]
        EKG1 --> EKG2 --> EKG3 --> EKG4
    end
    
    SKG4 --> Combined["Combined Intelligence"]
    EKG4 --> Combined
    
    style SKG3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style EKG3 fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style Combined fill:#fff8e1,stroke:#f57f17,stroke-width:3px
```

### When to use which

| Question Type | Best Approach | Why |
|---|---|---|
| "What are the payment terms for Vendor X?" | Structured Graph | Precise traversal through known schema |
| "Show the contract family tree for MSA-123" | Structured Graph | Hierarchy is explicit in edges |
| "What are common themes in high-risk clauses?" | Statistical Graph (GraphRAG) | Requires corpus-wide pattern detection |
| "How do IP terms vary across industries?" | Statistical Graph (GraphRAG) | Cross-document thematic analysis |
| "Find clauses about data breach notification" | Vector Search | Semantic similarity matching |
| "Total contract value by vendor" | Structured Graph + SQL | Aggregation over structured data |

---

## 3. Choosing Your Graph Strategy

Not every project needs both approaches. Here's a decision framework:

```mermaid
flowchart TD
    Start["What does your<br/>domain look like?"]
    
    Start --> Q1{"Do you have a<br/>well-defined schema?<br/>(entity types, relationships)"}
    
    Q1 -->|"Yes — contracts, invoices,<br/>org charts, supply chains"| Structured["✅ Structured Knowledge Graph<br/>Apache AGE / Neo4j + SQL"]
    
    Q1 -->|"No — research papers,<br/>news articles, general docs"| Statistical["✅ Statistical Graph (GraphRAG)<br/>Auto-extracted entities + communities"]
    
    Q1 -->|"Partially — some known<br/>structure, some discovery"| Both["✅ Both: Dual-Engine<br/>Structured for precision<br/>Statistical for discovery"]
    
    Structured --> Q2{"Need corpus-wide<br/>pattern analysis?"}
    Q2 -->|Yes| Both
    Q2 -->|No| StructuredOnly["Structured Graph Only<br/>+ Vector Search"]
    
    Statistical --> Q3{"Need precise<br/>field-level queries?"}
    Q3 -->|Yes| Both
    Q3 -->|No| StatisticalOnly["GraphRAG Only<br/>+ Vector Search"]
    
    style Both fill:#fff8e1,stroke:#f57f17,stroke-width:3px
    style StructuredOnly fill:#e8f5e9,stroke:#2e7d32
    style StatisticalOnly fill:#f3e5f5,stroke:#6a1b9a
```

### The dual-engine sweet spot

Domains with **rich internal structure AND need for cross-document discovery** benefit most from both engines:

- **Legal contracts** — structured hierarchies + thematic risk patterns
- **Healthcare records** — coded diagnoses + treatment pattern discovery
- **Financial filings** — structured line items + industry trend analysis
- **Supply chain** — known vendor relationships + hidden dependency patterns

---

## 4. Architecture: The Dual-Engine Pattern

The architecture places an **AI router agent** in front of two specialized engines, each optimized for different query types:

```mermaid
graph TB
    User["👤 User<br/>'Natural Language Question'"]
    
    subgraph Router["🧠 AI Router Agent"]
        Classify["Classify Query Intent"]
        Score["Score: Structured vs Statistical"]
        Decide["Route to Best Engine(s)"]
        Classify --> Score --> Decide
    end
    
    subgraph StructuredEngine["📊 Structured Engine"]
        SQL["SQL Generator<br/>Aggregation, filtering, joins"]
        Cypher["Cypher Generator<br/>Multi-hop graph traversal"]
        VecSearch["Vector Search<br/>Semantic similarity"]
    end
    
    subgraph StatisticalEngine["🌐 Statistical Engine (GraphRAG)"]
        Local["Local Search<br/>Entity-centric, focused"]
        Global["Global Search<br/>Community summaries, broad"]
        Drift["DRIFT Search<br/>Adaptive follow-up exploration"]
    end
    
    subgraph Response["📋 Response Layer"]
        Synthesize["Synthesize + Visualize"]
        Viz["Auto-Generated Charts<br/>Tables, Trees, Graphs"]
    end
    
    User --> Router
    Decide -->|"Specific entities,<br/>aggregation, hierarchy"| StructuredEngine
    Decide -->|"Patterns, themes,<br/>strategic analysis"| StatisticalEngine
    Decide -->|"Both needed"| StructuredEngine
    Decide -->|"Both needed"| StatisticalEngine
    StructuredEngine --> Response
    StatisticalEngine --> Response
    Response --> User
    
    style User fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Router fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    style StructuredEngine fill:#e8f5e9,stroke:#2e7d32
    style StatisticalEngine fill:#f3e5f5,stroke:#6a1b9a
    style Response fill:#fce4ec,stroke:#c62828
```

### Key design principles

1. **Single natural language interface** — Users never need to know which engine answers
2. **Router is an AI agent** — Not rule-based; it reasons about query intent
3. **Engines are independent** — Each can be deployed, scaled, and tested separately
4. **Shared data layer** — Both engines read from the same source of truth
5. **Response synthesis** — Results from either/both engines are unified before delivery

---

## 5. Data Ingestion: From Documents to Graphs

The ingestion pipeline is the most critical (and complex) part. It transforms unstructured documents into structured, queryable knowledge.

```mermaid
flowchart LR
    subgraph Input["📁 Input"]
        Docs["Raw Documents<br/>PDF, Markdown, DOCX"]
    end
    
    subgraph Extract["🔬 LLM Extraction"]
        Meta["Extract Metadata<br/>titles, dates, types, parties"]
        Segment["Segment into Sections"]
        Classify["Classify & Analyze<br/>each section"]
        Embed["Generate Embeddings"]
        Meta --> Segment --> Classify --> Embed
    end
    
    subgraph Transform["⚙️ Transform"]
        Resolve["Entity Resolution<br/>deduplicate parties/orgs"]
        Link["Link Relationships<br/>parent→child hierarchies"]
        Resolve --> Link
    end
    
    subgraph Load["💾 Load"]
        Relational["Relational Tables<br/>(SQL)"]
        Graph["Property Graph<br/>(Cypher)"]
        Vectors["Vector Indexes<br/>(Embeddings)"]
        KG["Knowledge Graph<br/>(GraphRAG Communities)"]
    end
    
    Input --> Extract
    Extract --> Transform
    Transform --> Relational
    Transform --> Graph
    Transform --> Vectors
    Docs -.->|"Separate pipeline"| KG
    
    style Input fill:#e3f2fd,stroke:#1565c0
    style Extract fill:#fff8e1,stroke:#f57f17
    style Transform fill:#f3e5f5,stroke:#6a1b9a
    style Load fill:#e8f5e9,stroke:#2e7d32
```

### The extraction challenge

LLM extraction is **the hardest step to get right**. Key considerations:

| Challenge | Approach |
|---|---|
| **Schema adherence** | Use structured outputs (JSON mode / Pydantic models) to enforce schema |
| **Consistency across documents** | Provide few-shot examples in prompts with exact field definitions |
| **Entity resolution** | Normalize names + fuzzy matching (e.g., "Acme Corp." = "Acme Corporation Inc.") |
| **Relationship inference** | Extract explicit references (parent contract IDs) + infer from context |
| **Scale** | Parallel processing with rate limiting; batch embedding calls |
| **Cost** | Segment documents first, then classify sections — avoids sending full docs to expensive models |

### Ingestion modes

A mature pipeline supports multiple modes for different operational needs:

```mermaid
graph LR
    subgraph Modes["Pipeline Modes"]
        Both["🔄 Both<br/>Full dual ingestion"]
        PG["📊 Structured Only<br/>SQL + Graph"]
        GR["🌐 GraphRAG Only<br/>Knowledge communities"]
        BYOG["🔗 BYOG<br/>Bring Your Own Graph<br/>Reuse structured graph<br/>for community detection"]
    end
    
    style Both fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    style BYOG fill:#e8eaf6,stroke:#283593,stroke-width:2px
```

The **BYOG** (Bring Your Own Graph) mode is particularly interesting — it avoids duplicate LLM extraction costs by reusing the structured graph's entities and relationships as input to GraphRAG's community detection algorithm.

---

## 6. The Structured Knowledge Graph

This is the **precision engine** — a schema-driven property graph stored in a database that supports both SQL and Cypher queries.

### Schema design principles

```mermaid
erDiagram
    DOCUMENT ||--o{ SECTION : contains
    DOCUMENT ||--o{ DOCUMENT_RELATIONSHIP : "parent/child"
    SECTION ||--o{ ENTITY_MENTION : references
    SECTION ||--o{ EXTRACTED_FACT : contains
    ENTITY ||--o{ ENTITY_MENTION : mentioned_in
    ENTITY ||--o{ EXTRACTED_FACT : involved_in
    
    DOCUMENT {
        uuid id PK
        string identifier UK
        string type
        string status
        date effective_date
    }
    
    ENTITY {
        uuid id PK
        string name
        string canonical_name
        string entity_type
    }
    
    SECTION {
        uuid id PK
        uuid document_id FK
        string label
        text content
        vector embedding
        string risk_level
    }
    
    EXTRACTED_FACT {
        uuid id PK
        uuid section_id FK
        string fact_type
        text description
        jsonb metadata
    }
```

> **Design tip:** Keep your relational schema normalized but your graph schema denormalized. Graphs shine with **redundant properties on nodes** that avoid joins during traversal.

### Why a property graph on PostgreSQL?

Instead of a standalone graph database, using a **graph extension on your existing RDBMS** offers:

| Benefit | Detail |
|---|---|
| **Single infrastructure** | No separate Neo4j/Neptune cluster to manage |
| **SQL + Cypher in one** | Aggregation via SQL, traversal via Cypher, on the same data |
| **Shared vectors** | pgvector embeddings accessible from both SQL and graph queries |
| **ACID transactions** | Graph mutations are transactional with the rest of your data |
| **Familiar tooling** | Standard PostgreSQL monitoring, backup, connection pooling |

### Graph query patterns

The graph layer enables **multi-hop traversals** that would require complex recursive CTEs in pure SQL:

```mermaid
graph LR
    P["👤 Party<br/>'Acme Corp'"] -->|IS_PARTY_TO| C["📋 Contract<br/>'MSA-001'"]
    C -->|CONTAINS| CL["📄 Clause<br/>'Liability'"]
    CL -->|IMPOSES| O["⚖️ Obligation<br/>'Maintain $5M coverage'"]
    P -->|RESPONSIBLE_FOR| O
    C -->|PARENT_OF| SOW["📋 SOW-001"]
    SOW -->|PARENT_OF| AMD["📋 AMD-001"]
    
    style P fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    style C fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style O fill:#ffebee,stroke:#c62828,stroke-width:2px
```

**Example traversals:**
- "All obligations for Party X across all contracts" → 3-hop traversal
- "Contract family tree for MSA-001" → recursive parent-child traversal
- "Parties sharing contracts with high-risk clauses" → pattern matching

---

## 7. The Statistical Knowledge Graph (GraphRAG)

Microsoft GraphRAG takes a fundamentally different approach. Instead of a pre-defined schema, it **auto-extracts entities and relationships**, then uses **community detection** to discover latent structure.

```mermaid
flowchart TB
    subgraph Phase1["Phase 1: Extraction"]
        Docs2["Documents"] --> Chunk["Chunk into<br/>Text Units"]
        Chunk --> Extract2["LLM: Extract<br/>Entities & Relationships"]
        Extract2 --> RawGraph["Raw Entity Graph<br/>thousands of nodes"]
    end
    
    subgraph Phase2["Phase 2: Community Detection"]
        RawGraph --> Leiden["Leiden Algorithm<br/>Cluster entities into<br/>communities"]
        Leiden --> Communities["Communities<br/>Groups of related entities"]
    end
    
    subgraph Phase3["Phase 3: Summarization"]
        Communities --> Summarize["LLM: Generate<br/>Community Reports"]
        Summarize --> Reports["Community Reports<br/>Thematic summaries"]
    end
    
    subgraph Phase4["Phase 4: Query"]
        Query["User Query"]
        Reports --> MapReduce["Map-Reduce<br/>over relevant reports"]
        Query --> MapReduce
        MapReduce --> Answer["Synthesized Answer<br/>with global context"]
    end
    
    style Phase1 fill:#e3f2fd,stroke:#1565c0
    style Phase2 fill:#f3e5f5,stroke:#6a1b9a
    style Phase3 fill:#fff8e1,stroke:#f57f17
    style Phase4 fill:#e8f5e9,stroke:#2e7d32
```

### How community detection works

The Leiden algorithm groups densely connected entities into communities — think of them as **"topics" that emerge from the data**:

```mermaid
graph TB
    subgraph Community1["🏘️ Community: IP & Licensing"]
        E1["Intellectual Property"]
        E2["Work Product"]
        E3["Background IP"]
        E4["License Grant"]
        E1 --- E2
        E2 --- E3
        E3 --- E4
        E4 --- E1
    end
    
    subgraph Community2["🏘️ Community: Risk & Liability"]
        E5["Indemnification"]
        E6["Limitation of Liability"]
        E7["Insurance Requirements"]
        E8["Warranty Disclaimer"]
        E5 --- E6
        E6 --- E7
        E7 --- E8
        E8 --- E5
    end
    
    subgraph Community3["🏘️ Community: Operational"]
        E9["Service Level Agreement"]
        E10["Change Management"]
        E11["Acceptance Criteria"]
        E9 --- E10
        E10 --- E11
    end
    
    E1 -.-|"weak link"| E5
    E9 -.-|"weak link"| E7
    
    style Community1 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Community2 fill:#ffebee,stroke:#c62828,stroke-width:2px
    style Community3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

### Search modes

GraphRAG offers multiple search strategies:

| Mode | How It Works | Best For |
|---|---|---|
| **Local Search** | Find relevant entities → retrieve their community context | Focused questions about specific topics |
| **Global Search** | Map-Reduce across ALL community reports | Broad "what are the themes" questions |
| **DRIFT Search** | Iterative follow-up queries with adaptive depth | Exploratory analysis |
| **Basic Search** | Fast keyword-style retrieval with concurrency | High-throughput simple lookups |

---

## 8. Agentic Query Routing

The "agentic" in "Agentic Graph RAG" means the system **reasons about how to answer** rather than blindly searching:

```mermaid
flowchart TD
    Q["User: 'What are the payment terms<br/>with Acme across all contracts?'"]
    
    subgraph Agent["🧠 Router Agent Reasoning"]
        Think1["1️⃣ Mentions specific party → needs entity lookup"]
        Think2["2️⃣ 'Payment terms' → structured financial data"]
        Think3["3️⃣ 'Across all contracts' → aggregation needed"]
        Think4["4️⃣ Decision: SQL with JOINs through party→contract→clause"]
        Think1 --> Think2 --> Think3 --> Think4
    end
    
    Q --> Agent
    
    Agent -->|Route| SQL2["SQL Query:<br/>SELECT ... FROM parties<br/>JOIN contracts<br/>JOIN clauses<br/>WHERE party.name = 'Acme'<br/>AND clause_type = 'Payment Terms'"]
    
    SQL2 --> Result["Structured Result<br/>with exact amounts, dates, currencies"]
    
    style Q fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Agent fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    style Result fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

### Building a decision tree

Rather than vague instructions, give the agent a **precise numbered decision tree**:

```
STEP 1: Does the query ask about MEANING, THEMES, or PATTERNS
        across many documents?
   YES → Use GraphRAG (Global Search)
   NO  → Continue to Step 2

STEP 2: Does the query mention SPECIFIC entities by name
        or ask for SPECIFIC facts (dates, amounts, counts)?
   YES → Use Structured Engine (SQL or Cypher)
   NO  → Continue to Step 3

STEP 3: Does the query ask about RELATIONSHIPS or PATHS
        between entities (hierarchies, connections)?
   YES → Use Cypher (graph traversal)
   NO  → Continue to Step 4

STEP 4: Does the query use CONCEPTUAL language
        ("clauses like...", "similar to...")?
   YES → Use Vector Search (semantic similarity)
   NO  → Default to SQL
```

### Agent as a tool-calling LLM

The agent pattern uses the LLM as a **reasoning engine** that selects and orchestrates tools:

```mermaid
sequenceDiagram
    participant User
    participant Agent as 🧠 AI Agent
    participant SQL as SQL Tool
    participant Cypher as Cypher Tool
    participant Vector as Vector Tool
    participant LLM as LLM (Synthesis)
    
    User->>Agent: "Show contract family tree for MSA-001"
    
    Note over Agent: Reasoning: hierarchy query → Cypher
    
    Agent->>SQL: get_contract_id('MSA-001')
    SQL-->>Agent: contract_id = 'contract_197'
    
    Agent->>Cypher: MATCH (parent)<--(child) WHERE parent.id = ...
    Cypher-->>Agent: [{child: SOW-001}, {child: AMD-001}, ...]
    
    Agent->>LLM: Format results as Mermaid tree diagram
    LLM-->>Agent: ```mermaid graph TD ...```
    
    Agent->>User: Here's the family tree: [visualization]
```

> **Key insight:** The agent may make **multiple tool calls** to answer one question. For example, looking up an identifier via SQL before using it in a Cypher query. This multi-step reasoning is what makes it "agentic."

---

## 9. Vector Search in a Graph World

Vector search and graph queries are **complementary, not competing**:

```mermaid
graph TB
    subgraph VectorDomain["🔍 Vector Search Domain"]
        VS1["'Find clauses about data breach notification'"]
        VS2["'Limitation of liability clauses like Acme's'"]
        VS3["Fuzzy, conceptual, 'similar to' queries"]
    end
    
    subgraph GraphDomain["🔗 Graph Query Domain"]
        GQ1["'All obligations for Party X'"]
        GQ2["'Contract family tree for MSA-001'"]
        GQ3["Exact, structural, relationship queries"]
    end
    
    subgraph Overlap["🔄 Hybrid Queries"]
        HQ1["'High-risk clauses similar to our<br/>IP provisions with Vendor Y'"]
        HQ2["Vector search → filter by graph context"]
    end
    
    VectorDomain --> Overlap
    GraphDomain --> Overlap
    
    style VectorDomain fill:#e3f2fd,stroke:#1565c0
    style GraphDomain fill:#e8f5e9,stroke:#2e7d32
    style Overlap fill:#fff8e1,stroke:#f57f17,stroke-width:2px
```

### Shared vector store pattern

A powerful pattern is storing vectors **in the same database** as your structured and graph data:

```
┌─────────────────────────────────────────────────┐
│              PostgreSQL                          │
│                                                  │
│  📊 Relational Tables    (SQL queries)           │
│  🔗 Property Graph       (Cypher queries)        │
│  🔍 Vector Indexes       (Similarity search)     │
│  🌐 GraphRAG Vectors     (Entity embeddings)     │
│                                                  │
│  → One database. One connection. Full power.     │
└─────────────────────────────────────────────────┘
```

**Benefits of co-located vectors:**
- Filter vector results by graph context (e.g., "similar clauses, but only in active contracts")
- Enrich vector results with structured metadata without additional queries
- Single infrastructure to deploy, monitor, and back up

---

## 10. Key Challenges & Lessons Learned

### Challenge 1: Entity Resolution

The same entity appears differently across documents:

```
"Acme Corporation, Inc."  →  canonical: "acme corporation"
"ACME CORP."              →  canonical: "acme"  (fuzzy match → same entity)
"Acme Corp"               →  canonical: "acme"  (fuzzy match → same entity)
```

**Solution:** Two-layer resolution:
1. **Normalization** — strip legal suffixes, lowercase, remove punctuation
2. **Fuzzy matching** — trigram similarity (pg_trgm) with threshold ≥ 0.8

### Challenge 2: Graph Schema vs. SQL Schema Mismatch

Property names differ between SQL tables and graph nodes:

| Concept | SQL Column | Graph Property |
|---|---|---|
| Contract ID | `contract_identifier` | `identifier` |
| Contract type | `contract_type` | `type` |
| Clause section | `section_label` | `section` |

**Solution:** Document the mapping explicitly and teach the AI agent about it in the system prompt.

### Challenge 3: LLM Extraction Consistency

LLMs extract slightly different structures from similar documents.

**Solutions:**
- Use **structured outputs** (JSON schema / Pydantic models) to enforce format
- Provide **domain-specific extraction prompts** with examples
- **Post-validate** extracted data against the schema before insertion
- Run extraction in **parallel with rate limiting** for throughput

### Challenge 4: Custom Prompt Maintenance

When using frameworks like GraphRAG, default prompts are generic. Domain-specific prompts dramatically improve quality but **must be maintained across version upgrades**.

> **Lesson:** Custom prompts are living documents. Track them in version control and test them with each framework upgrade.

### Challenge 5: Graph Query Generation

LLMs sometimes generate invalid Cypher queries. Common mistakes:

| Mistake | Fix |
|---|---|
| Wrong property names | Include property mapping in the system prompt |
| Unsupported operators | List supported operators explicitly |
| Missing graph path setup | Include boilerplate in prompt templates |
| Over-complex queries | Teach the agent to decompose into multiple simpler queries |

```mermaid
flowchart LR
    Bad["❌ LLM generates<br/>one complex Cypher query<br/>that fails"] 
    
    Good["✅ LLM decomposes into:<br/>1. SQL lookup (get ID)<br/>2. Simple Cypher (traverse)<br/>3. Format results"]
    
    Bad -.->|"Better approach"| Good
    
    style Bad fill:#ffebee,stroke:#c62828
    style Good fill:#e8f5e9,stroke:#2e7d32
```

---

## 11. Production Considerations

### Infrastructure

```mermaid
graph TB
    subgraph Cloud["☁️ Cloud Infrastructure"]
        LB["Load Balancer / Ingress"]
        
        subgraph Compute["Container Orchestration"]
            API["API Server<br/>(FastAPI)"]
            API2["API Server<br/>(replica)"]
        end
        
        subgraph Data["Data Layer"]
            PG[("PostgreSQL<br/>+ pgvector<br/>+ Graph Extension")]
        end
        
        subgraph AI["AI Services"]
            LLM2["LLM Endpoint<br/>(Chat + Reasoning)"]
            EMB["Embedding Endpoint"]
        end
    end
    
    Users["👥 Users"] --> LB
    LB --> API
    LB --> API2
    API --> PG
    API2 --> PG
    API -.-> LLM2
    API -.-> EMB
    API2 -.-> LLM2
    API2 -.-> EMB
    
    style PG fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style LLM2 fill:#ffebee,stroke:#c62828
    style Users fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
```

### Cost optimization

| Strategy | Impact |
|---|---|
| **Cache LLM responses** | Avoid re-extracting identical documents |
| **Batch embedding calls** | Reduce API round-trips |
| **BYOG mode** | Reuse structured graph for GraphRAG — avoids duplicate extraction |
| **Tiered models** | Use smaller models for classification, larger for extraction |
| **Incremental ingestion** | Only process new/changed documents |

### Monitoring

Key metrics to track:

- **Query routing accuracy** — Is the router sending queries to the right engine?
- **Query latency by type** — SQL vs. Cypher vs. Vector vs. GraphRAG response times
- **LLM token usage** — Per-query and per-ingestion costs
- **Graph size growth** — Nodes and edges over time
- **Entity resolution hit rate** — How often fuzzy matching prevents duplicates

### Security

- **Never expose raw SQL/Cypher to users** — The AI agent generates queries, but users interact via natural language only
- **Parameterize queries** — Prevent injection through agent-generated queries
- **Row-level security** — Use PostgreSQL RLS policies for multi-tenant deployments
- **Secret management** — API keys in environment variables or secret stores, never in code

---

## Summary: The Pattern at a Glance

```mermaid
graph TB
    subgraph "1. INGEST"
        I1["📄 Documents"]
        I2["🔬 LLM Extraction"]
        I3["🔗 Entity Resolution"]
        I1 --> I2 --> I3
    end
    
    subgraph "2. STORE"
        S1["📊 SQL Tables"]
        S2["🔗 Property Graph"]
        S3["🔍 Vector Index"]
        S4["🌐 GraphRAG Communities"]
    end
    
    subgraph "3. QUERY"
        Q2["🧠 AI Agent Router"]
        Q3["📊 SQL"]
        Q4["🔗 Cypher"]
        Q5["🔍 Semantic Search"]
        Q6["🌐 Community Search"]
        Q2 --> Q3
        Q2 --> Q4
        Q2 --> Q5
        Q2 --> Q6
    end
    
    subgraph "4. RESPOND"
        R1["💬 Natural Language Answer"]
        R2["📊 Auto-Generated Visualizations"]
    end
    
    I3 --> S1
    I3 --> S2
    I3 --> S3
    I3 --> S4
    
    S1 --> Q3
    S2 --> Q4
    S3 --> Q5
    S4 --> Q6
    
    Q3 --> R1
    Q4 --> R1
    Q5 --> R1
    Q6 --> R1
    R1 --> R2
    
    style I1 fill:#e3f2fd,stroke:#1565c0
    style Q2 fill:#fff8e1,stroke:#f57f17,stroke-width:3px
    style R2 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

### Key takeaways

1. **Graphs preserve structure** that flat RAG discards — hierarchies, relationships, provenance
2. **Two graph approaches** serve different needs: structured (precision) vs. statistical (discovery)
3. **Agentic routing** lets a single natural language interface select the best query strategy
4. **Co-locate everything** in one database when possible — SQL, graph, vectors
5. **Entity resolution** is the unsung hero — without it, your graph is full of duplicates
6. **Custom prompts** for your domain make the difference between demo and production quality
7. **Start with the structured graph** — it delivers immediate value; add GraphRAG when you need corpus-wide pattern discovery

---

> **Next:** Explore the [Contract Intelligence Platform](contract_intelligence/README.md) to see these patterns implemented in a production system for legal contract analysis.
