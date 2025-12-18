# 🧠 Content Intelligence Platform

> **A configurable, AI-powered framework for transforming domain-specific documents into queryable knowledge graphs with deep cross-document intelligence**

---

## 🎯 Vision

Traditional document processing treats each document in isolation. **Content Intelligence Platform** breaks this paradigm by:

1. **Understanding your domain** through AI-assisted schema generation
2. **Extracting structured knowledge** from unstructured content
3. **Building rich relationship graphs** that reveal hidden connections
4. **Enabling natural language queries** across your entire corpus

The platform is **domain-agnostic by design** — whether you're analyzing contracts, research papers, medical records, or financial reports, the same powerful infrastructure adapts to your specific ontology.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           CONTENT INTELLIGENCE PLATFORM                                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: SCHEMA GENERATION (AI-Assisted)                                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐                   │
│   │  Sample Documents│   │  Business Goals  │   │  Sample Questions│                   │
│   │  (5-10 examples) │   │  & Requirements  │   │  Users Will Ask  │                   │
│   └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘                   │
│            │                      │                      │                              │
│            └──────────────────────┼──────────────────────┘                              │
│                                   ▼                                                     │
│                    ┌──────────────────────────────┐                                     │
│                    │   🤖 Schema Generation AI    │                                     │
│                    │   • Analyzes document types  │                                     │
│                    │   • Identifies entities      │                                     │
│                    │   • Discovers relationships  │                                     │
│                    │   • Suggests properties      │                                     │
│                    └──────────────┬───────────────┘                                     │
│                                   ▼                                                     │
│                    ┌──────────────────────────────┐                                     │
│                    │   📋 Graph Schema (Editable) │  ◄── YAML/JSON output               │
│                    │   • Ontology definition      │      Human-reviewable               │
│                    │   • Entity specifications    │      Version controlled             │
│                    │   • Relationship types       │                                     │
│                    │   • Property schemas         │                                     │
│                    │   • Extraction prompts       │                                     │
│                    └──────────────────────────────┘                                     │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: INFRASTRUCTURE GENERATION                                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   Graph Schema ───► ┌──────────────────────────────────────────────────────────────┐   │
│                     │                                                              │   │
│                     │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │   │
│                     │  │ PostgreSQL     │  │ Apache AGE     │  │ Extraction     │ │   │
│                     │  │ Schema (DDL)   │  │ Graph Schema   │  │ Prompts        │ │   │
│                     │  │                │  │                │  │                │ │   │
│                     │  │ • Tables       │  │ • Node labels  │  │ • Per entity   │ │   │
│                     │  │ • Columns      │  │ • Edge types   │  │ • Per relation │ │   │
│                     │  │ • Indexes      │  │ • Properties   │  │ • Validation   │ │   │
│                     │  │ • Constraints  │  │ • Constraints  │  │ • Examples     │ │   │
│                     │  └────────────────┘  └────────────────┘  └────────────────┘ │   │
│                     │                                                              │   │
│                     └──────────────────────────────────────────────────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: CONTENT INGESTION                                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   ┌─────────────────┐                                                                   │
│   │ Raw Documents   │    Unstructured: PDFs, Markdown, Text, HTML, DOCX                 │
│   │ (Any Format)    │    Structured: Tables, CSVs, JSON, XML                            │
│   └────────┬────────┘                                                                   │
│            │                                                                            │
│            ▼                                                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────┐      │
│   │                         INGESTION PIPELINE                                   │      │
│   │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │      │
│   │  │ Document    │ → │ LLM Entity  │ → │ Entity      │ → │ Graph       │      │      │
│   │  │ Parsing     │   │ Extraction  │   │ Resolution  │   │ Construction│      │      │
│   │  │             │   │ (Schema-    │   │ (Fuzzy      │   │ (AGE Nodes  │      │      │
│   │  │ • Text      │   │  guided)    │   │  Dedup)     │   │  & Edges)   │      │      │
│   │  │ • Tables    │   │             │   │             │   │             │      │      │
│   │  │ • Structure │   │             │   │             │   │             │      │      │
│   │  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘      │      │
│   │         │                                                    │              │      │
│   │         ▼                                                    ▼              │      │
│   │  ┌─────────────┐                                      ┌─────────────┐      │      │
│   │  │ Embeddings  │                                      │ PostgreSQL  │      │      │
│   │  │ (pgvector)  │                                      │ + AGE Graph │      │      │
│   │  └─────────────┘                                      └─────────────┘      │      │
│   └─────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: INTELLIGENT QUERY                                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   User: "What are the key risks across all our vendor relationships?"                   │
│                                                                                         │
│            │                                                                            │
│            ▼                                                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────┐      │
│   │                         QUERY AGENT LAYER                                    │      │
│   │                                                                              │      │
│   │  ┌──────────────────────────────────────────────────────────────────────┐   │      │
│   │  │  🤖 Router Agent                                                      │   │      │
│   │  │  • Understands graph schema (ontology context)                        │   │      │
│   │  │  • Routes to appropriate query strategy                               │   │      │
│   │  │  • Synthesizes multi-source results                                   │   │      │
│   │  └──────────────────────────────────────────────────────────────────────┘   │      │
│   │                    │                   │                   │                │      │
│   │                    ▼                   ▼                   ▼                │      │
│   │  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐      │      │
│   │  │  SQL Agent         │ │  Graph Agent       │ │  Semantic Agent    │      │      │
│   │  │  • Aggregations    │ │  • Cypher queries  │ │  • Vector search   │      │      │
│   │  │  • Joins           │ │  • Path finding    │ │  • Similarity      │      │      │
│   │  │  • Filtering       │ │  • Multi-hop       │ │  • Conceptual      │      │      │
│   │  └────────────────────┘ └────────────────────┘ └────────────────────┘      │      │
│   │                                                                              │      │
│   └─────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Graph Schema Definition

The heart of the platform is the **Graph Schema** — a human-readable, AI-generated, and fully editable specification that drives everything.

### Schema Structure (YAML Format)

```yaml
# content_intelligence_schema.yaml

metadata:
  name: "Contract Intelligence"
  version: "1.0.0"
  domain: "Legal/Contracts"
  description: "Schema for analyzing enterprise contract portfolios"

# Ontology: High-level conceptual model
ontology:
  core_concepts:
    - name: "Contract"
      description: "Legal agreement between parties"
      is_document: true  # This is a primary document type
      
    - name: "Party"
      description: "Organization or individual in a contract"
      is_document: false  # Extracted entity
      
    - name: "Obligation"
      description: "Duty or requirement imposed by a contract"
      is_document: false

  relationships:
    - name: "IS_PARTY_TO"
      from: "Party"
      to: "Contract"
      cardinality: "many-to-many"
      
    - name: "CONTAINS"
      from: "Contract"
      to: "Clause"
      cardinality: "one-to-many"

# Entity Definitions: Detailed specifications
entities:
  Contract:
    description: "A legal agreement document"
    table_name: "contracts"
    properties:
      - name: "identifier"
        type: "string"
        required: true
        unique: true
        description: "Unique contract identifier (e.g., MSA-2024-001)"
        extraction_hint: "Look for contract number, reference, or ID"
        
      - name: "title"
        type: "string"
        required: true
        max_length: 500
        
      - name: "contract_type"
        type: "enum"
        values: ["Master Services Agreement", "Statement of Work", "Amendment", "NDA"]
        
      - name: "effective_date"
        type: "date"
        extraction_hint: "The date the contract becomes effective"
        
      - name: "total_value"
        type: "decimal"
        
      - name: "full_text"
        type: "text"
        embed: true  # Generate vector embedding
        
    extraction_prompt: |
      Extract the following contract metadata from the document:
      - Contract identifier/reference number
      - Title of the agreement
      - Type of contract (MSA, SOW, Amendment, etc.)
      - Effective and expiration dates
      - Total contract value if specified
      - Governing law/jurisdiction
      
  Party:
    description: "An organization or individual"
    table_name: "parties"
    properties:
      - name: "name"
        type: "string"
        required: true
        
      - name: "canonical_name"
        type: "string"
        derived: true
        normalization: "entity_name"  # Apply standard normalization
        
      - name: "party_type"
        type: "enum"
        values: ["Corporation", "Individual", "Government", "Non-Profit"]
        
    entity_resolution:
      enabled: true
      method: "fuzzy"
      threshold: 0.8
      index_type: "trigram"

# Relationship Definitions
relationships:
  IS_PARTY_TO:
    from_entity: "Party"
    to_entity: "Contract"
    properties:
      - name: "role"
        type: "enum"
        values: ["Client", "Vendor", "Licensor", "Licensee"]
    extraction_prompt: |
      Identify all parties mentioned in this contract and their roles.
      
  AMENDS:
    from_entity: "Contract"
    to_entity: "Contract"
    properties:
      - name: "amendment_date"
        type: "date"
    extraction_hint: "Look for 'amends', 'modifies', or references to parent agreements"

# Extraction Configuration
extraction:
  llm_model: "gpt-4.1"
  embedding_model: "text-embedding-3-small"
  embedding_dimensions: 1536
  chunk_size: 4000
  overlap: 200

# Query Agent Context
query_context:
  domain_description: |
    This is a contract intelligence system for analyzing enterprise legal agreements.
    Users will ask questions about contract terms, party relationships, obligations,
    financial terms, and risk exposure across the portfolio.
    
  sample_questions:
    - "What are our highest risk clauses across all vendor contracts?"
    - "Show the contract family tree for Acme Corp MSA"
    - "Which contracts expire in Q2 2025?"
    - "Total contract value by vendor"
    
  query_patterns:
    aggregation: ["total", "count", "average", "sum by"]
    graph_traversal: ["connected to", "related to", "hierarchy", "family tree"]
    semantic: ["similar to", "like", "about", "themed"]
```

---

## 🤖 Schema Generation AI

The platform includes an AI assistant that helps generate optimal graph schemas:

### Input Requirements

| Input | Description | Example |
|-------|-------------|---------|
| **Sample Documents** | 5-10 representative documents | Contract PDFs, research papers |
| **Business Goals** | What insights do you need? | "Understand vendor risk exposure" |
| **Sample Questions** | Questions users will ask | "Which contracts have unlimited liability?" |
| **Domain Context** | Industry/domain knowledge | "Enterprise legal department" |

### Generation Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SCHEMA GENERATION WORKFLOW                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  1. DOCUMENT ANALYSIS
     ┌─────────────────────────────────────────────────────────────────────┐
     │  AI analyzes sample documents to identify:                          │
     │  • Document types and structures                                    │
     │  • Recurring entities (people, orgs, concepts)                      │
     │  • Implicit relationships between entities                          │
     │  • Key properties and attributes                                    │
     │  • Tables, lists, and structured data                               │
     └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  2. QUESTION ANALYSIS
     ┌─────────────────────────────────────────────────────────────────────┐
     │  AI analyzes sample questions to determine:                         │
     │  • Required entities to answer questions                            │
     │  • Necessary relationships for traversal                            │
     │  • Aggregation and filtering needs                                  │
     │  • Semantic search requirements                                     │
     └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  3. ONTOLOGY SYNTHESIS
     ┌─────────────────────────────────────────────────────────────────────┐
     │  AI synthesizes a coherent ontology:                                │
     │  • Core concepts and their hierarchy                                │
     │  • Relationship types with cardinality                              │
     │  • Property schemas with types and constraints                      │
     │  • Entity resolution strategies                                     │
     └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  4. PROMPT GENERATION
     ┌─────────────────────────────────────────────────────────────────────┐
     │  AI generates extraction prompts:                                   │
     │  • Entity-specific extraction instructions                          │
     │  • Relationship identification prompts                              │
     │  • Validation and normalization rules                               │
     │  • Few-shot examples from sample documents                          │
     └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  5. HUMAN REVIEW & REFINEMENT
     ┌─────────────────────────────────────────────────────────────────────┐
     │  Domain expert reviews and refines:                                 │
     │  • Adjusts entity definitions                                       │
     │  • Adds missing relationships                                       │
     │  • Refines extraction prompts                                       │
     │  • Validates against business requirements                          │
     └─────────────────────────────────────────────────────────────────────┘
```

---

## 💼 Business Scenarios

The Content Intelligence Platform can be applied across many domains:

### 1. 📜 Contract Intelligence (Reference Implementation)

**Domain:** Legal/Procurement

**Use Cases:**
- Cross-contract risk analysis
- Vendor relationship mapping
- Obligation tracking and compliance
- Contract family tree visualization
- Financial term aggregation

**Key Entities:** Contract, Party, Clause, Obligation, Right, Risk, Monetary Value

**Sample Questions:**
- "What are our highest risk clauses across all vendor contracts?"
- "Show all contracts with unlimited liability exposure"
- "Which vendors have the most favorable payment terms?"

---

### 2. 📚 Research & Academic Intelligence

**Domain:** Research/Academia

**Use Cases:**
- Literature review automation
- Citation network analysis
- Methodology pattern discovery
- Research gap identification
- Author collaboration mapping

**Key Entities:** Paper, Author, Institution, Methodology, Finding, Citation, Dataset

**Sample Questions:**
- "What methodologies are most commonly used for NLP evaluation?"
- "Show the citation network around transformer architecture papers"
- "Which institutions are leading in quantum computing research?"
- "Find research gaps in federated learning literature"

---

### 3. 🏥 Clinical & Healthcare Intelligence

**Domain:** Healthcare

**Use Cases:**
- Patient journey analysis
- Treatment outcome correlation
- Drug interaction discovery
- Clinical protocol compliance
- Care pathway optimization

**Key Entities:** Patient, Provider, Diagnosis, Treatment, Medication, Outcome, Protocol

**Sample Questions:**
- "What treatments show best outcomes for Type 2 diabetes patients over 65?"
- "Show all patients with potential drug interaction risks"
- "Which care protocols have highest compliance rates?"
- "Identify patterns in readmission cases"

---

### 4. 👥 HR & Talent Intelligence

**Domain:** Human Resources

**Use Cases:**
- Skills gap analysis
- Career path optimization
- Team composition insights
- Attrition pattern detection
- Training effectiveness measurement

**Key Entities:** Employee, Role, Skill, Project, Team, Certification, Performance Review

**Sample Questions:**
- "Which skills are most correlated with promotion to senior engineer?"
- "Show the career paths of our top performers"
- "What teams have the most diverse skill coverage?"
- "Identify flight risks based on performance and tenure patterns"

---

### 5. 🔗 Supply Chain Intelligence

**Domain:** Logistics/Procurement

**Use Cases:**
- Supplier risk assessment
- Dependency chain analysis
- Alternative supplier discovery
- Cost optimization pathways
- Compliance tracking

**Key Entities:** Supplier, Product, Component, Facility, Shipment, Contract, Risk Event

**Sample Questions:**
- "What's our exposure if Supplier X experiences disruption?"
- "Show all single-source dependencies in our supply chain"
- "Which alternative suppliers can provide Component Y?"
- "Trace the origin of all components in Product Z"

---

### 6. 📋 Regulatory & Compliance Intelligence

**Domain:** Compliance/Legal

**Use Cases:**
- Regulation mapping to controls
- Compliance gap analysis
- Audit evidence management
- Policy change impact assessment
- Cross-regulation overlap detection

**Key Entities:** Regulation, Requirement, Control, Evidence, Audit, Policy, Risk

**Sample Questions:**
- "Which controls satisfy both SOX and GDPR requirements?"
- "Show all gaps in our ISO 27001 compliance"
- "What evidence do we have for PCI-DSS Requirement 3?"
- "Impact analysis: What controls are affected by the new privacy law?"

---

### 7. 🎫 Customer Support Intelligence

**Domain:** Customer Service

**Use Cases:**
- Issue pattern recognition
- Knowledge base optimization
- Resolution path analysis
- Customer journey mapping
- Escalation prediction

**Key Entities:** Ticket, Customer, Product, Issue, Solution, Agent, Knowledge Article

**Sample Questions:**
- "What are the most common issues for Product X this quarter?"
- "Show the resolution paths for billing disputes"
- "Which knowledge articles need updating based on ticket patterns?"
- "Identify customers at risk of churn based on support history"

---

### 8. 💰 Financial Document Intelligence

**Domain:** Finance

**Use Cases:**
- Cross-filing analysis
- Entity relationship mapping
- Risk factor tracking
- Financial metric extraction
- Regulatory filing compliance

**Key Entities:** Filing, Company, Executive, Financial Metric, Risk Factor, Business Segment

**Sample Questions:**
- "Track revenue growth across all portfolio companies"
- "What risk factors are most commonly cited in our industry?"
- "Show executive turnover patterns correlated with stock performance"
- "Compare gross margins across competitors over 5 years"

---

### 9. 🔬 Patent & IP Intelligence

**Domain:** Intellectual Property

**Use Cases:**
- Prior art discovery
- Patent landscape mapping
- Innovation trend analysis
- Competitor IP monitoring
- Licensing opportunity identification

**Key Entities:** Patent, Claim, Inventor, Assignee, Citation, Technology Class

**Sample Questions:**
- "Find all patents related to our core technology that expire in 2025"
- "Show the citation network around our key patents"
- "What technology areas are seeing the most patent activity?"
- "Identify potential licensing targets in battery technology"

---

### 10. 🏢 M&A Due Diligence Intelligence

**Domain:** Corporate Development

**Use Cases:**
- Target company analysis
- Risk factor aggregation
- Synergy identification
- Integration planning
- Competitive landscape mapping

**Key Entities:** Company, Deal, Risk, Synergy, Financials, Contract, Employee

**Sample Questions:**
- "Aggregate all identified risks across the 500 documents in the data room"
- "What contracts require change of control consent?"
- "Show potential revenue synergies with our existing customer base"
- "Identify key personnel with non-compete agreements"

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Database** | PostgreSQL 16 | Relational storage, full-text search |
| **Graph** | Apache AGE | Cypher queries, relationship traversal |
| **Vector** | pgvector | Semantic similarity search |
| **Fuzzy Match** | pg_trgm | Entity resolution |
| **LLM** | Azure OpenAI | Extraction, schema generation, query agents |
| **Embeddings** | text-embedding-3-small | 1536-dimension vectors |
| **Backend** | FastAPI (Python) | API layer, agent orchestration |
| **Frontend** | React + TypeScript | User interface |
| **Infrastructure** | Azure Container Apps | Deployment |

---

## 📁 Repository Structure

```
content-intelligence/
├── README.md                      # This file
├── core/                          # Core platform (domain-agnostic)
│   ├── schema/                    # Schema definition & generation
│   │   ├── generator.py           # AI-assisted schema generator
│   │   ├── validator.py           # Schema validation
│   │   ├── models.py              # Pydantic schema models
│   │   └── templates/             # Base schema templates
│   ├── database/                  # Database generation
│   │   ├── postgres_generator.py  # Generate DDL from schema
│   │   ├── age_generator.py       # Generate graph schema
│   │   └── migration.py           # Schema migrations
│   ├── ingestion/                 # Ingestion pipeline
│   │   ├── pipeline.py            # Orchestration
│   │   ├── extractors/            # Entity extractors
│   │   ├── resolvers/             # Entity resolution
│   │   └── loaders/               # Database loaders
│   ├── agents/                    # Query agents
│   │   ├── router.py              # Query routing
│   │   ├── sql_agent.py           # SQL generation
│   │   ├── graph_agent.py         # Cypher generation
│   │   └── semantic_agent.py      # Vector search
│   └── api/                       # FastAPI endpoints
│       └── main.py
├── domains/                       # Domain-specific implementations
│   ├── contract_intelligence/     # Legal contracts (reference)
│   ├── research_intelligence/     # Academic papers
│   └── [your_domain]/             # Your custom domain
└── frontend/                      # React UI
```

---

## 🚀 Getting Started

### 1. Define Your Domain

Start by answering these questions:

- What documents will you analyze?
- What questions do users need to answer?
- What entities and relationships matter?
- What integrations are needed?

### 2. Generate Schema

```bash
# Interactive schema generation
python -m core.schema.generator \
  --samples ./my_documents/ \
  --questions ./sample_questions.txt \
  --context "Enterprise procurement department"
```

### 3. Review & Refine

Edit the generated `schema.yaml` to:
- Add missing entities
- Refine extraction prompts
- Adjust relationship definitions
- Configure entity resolution

### 4. Initialize Infrastructure

```bash
# Generate PostgreSQL schema and initialize
python -m core.database.postgres_generator --schema schema.yaml
python -m core.database.age_generator --schema schema.yaml
```

### 5. Ingest Content

```bash
# Run ingestion pipeline
python -m core.ingestion.pipeline \
  --schema schema.yaml \
  --input ./documents/
```

### 6. Query

```bash
# Start the API
uvicorn core.api.main:app --reload

# Or use the UI
cd frontend && npm run dev
```

---

## 🎯 Roadmap

### Phase 1: Foundation ✅
- [x] Contract Intelligence reference implementation
- [x] PostgreSQL + Apache AGE infrastructure
- [x] Entity resolution with fuzzy matching
- [x] Query agent layer

### Phase 2: Schema Framework (In Progress)
- [ ] YAML schema specification
- [ ] AI-assisted schema generator
- [ ] Schema-to-DDL compiler
- [ ] Schema-to-prompt compiler

### Phase 3: Multi-Domain Support
- [ ] Domain template library
- [ ] Custom entity types
- [ ] Pluggable extractors
- [ ] Domain-specific agents

### Phase 4: Enterprise Features
- [ ] Multi-tenant support
- [ ] Schema versioning & migration
- [ ] Incremental re-indexing
- [ ] Audit logging

---

## 📚 Implementations

| Domain | Status | Description |
|--------|--------|-------------|
| [Contract Intelligence](./contract_intelligence/) | ✅ Reference | Legal contract analysis with dual-graph (PostgreSQL + GraphRAG) |
| Research Intelligence | 🔜 Planned | Academic paper and citation analysis |
| Healthcare Intelligence | 🔜 Planned | Clinical document analysis |

---

## 🤝 Contributing

1. Fork the repository
2. Create a domain implementation in `domains/`
3. Share your schema templates
4. Submit a pull request

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details
