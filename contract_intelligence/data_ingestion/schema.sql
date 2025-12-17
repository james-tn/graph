-- Contract Intelligence Platform - PostgreSQL Schema

-- Enable pg_trgm extension for fuzzy matching / entity resolution
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop existing objects
DROP TABLE IF EXISTS extraction_jobs CASCADE;
DROP TABLE IF EXISTS risks CASCADE;
DROP TABLE IF EXISTS monetary_values CASCADE;
DROP TABLE IF EXISTS conditions CASCADE;
DROP TABLE IF EXISTS term_definitions CASCADE;
DROP TABLE IF EXISTS rights CASCADE;
DROP TABLE IF EXISTS obligations CASCADE;
DROP TABLE IF EXISTS clauses CASCADE;
DROP TABLE IF EXISTS contract_relationships CASCADE;
DROP TABLE IF EXISTS parties_contracts CASCADE;
DROP TABLE IF EXISTS parties CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;
DROP TABLE IF EXISTS jurisdictions CASCADE;
DROP TABLE IF EXISTS clause_types CASCADE;
DROP TABLE IF EXISTS risk_types CASCADE;
DROP TABLE IF EXISTS party_roles CASCADE;

-- Lookup tables
CREATE TABLE clause_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE risk_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    severity_default VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE party_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core entities
CREATE TABLE jurisdictions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,  -- Increased for formal legal jurisdiction names
    country VARCHAR(200),  -- Increased for formal country names
    state_province VARCHAR(200),  -- Increased for formal state/province names
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, country, state_province)
);

CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    contract_identifier VARCHAR(200) UNIQUE NOT NULL,
    reference_number VARCHAR(200),  -- E.g., MSA-ABC-202401-005, SOW-ABC-202403-012
    title TEXT NOT NULL,
    contract_type VARCHAR(200),
    effective_date DATE,
    expiration_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    governing_law VARCHAR(200),
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    term_type VARCHAR(50),
    risk_score_overall DECIMAL(3,2),
    source_file_path TEXT,
    source_markdown TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contract relationships table (parent-child, amendments, SOWs, etc.)
CREATE TABLE contract_relationships (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    child_contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    parent_contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    parent_reference_number VARCHAR(200),  -- Parent ref captured even if not yet ingested
    relationship_type VARCHAR(50) CHECK (relationship_type IN ('amendment', 'sow', 'addendum', 'work_order', 'maintenance', 'related')),
    relationship_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(child_contract_id, parent_contract_id, relationship_type)
);

CREATE TABLE parties (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    name VARCHAR(300) NOT NULL,  -- Display name (original)
    canonical_name VARCHAR(300) NOT NULL,  -- Normalized name for deduplication
    party_type VARCHAR(200),  -- Increased for longer party type descriptions
    address TEXT,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, canonical_name)  -- Dedupe on canonical name, not display name
);

CREATE TABLE parties_contracts (
    id SERIAL PRIMARY KEY,
    party_id INTEGER NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES party_roles(id),
    role_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(party_id, contract_id, role_id)
);

CREATE TABLE clauses (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    section_label TEXT,
    title TEXT,
    clause_type_id INTEGER REFERENCES clause_types(id),
    clause_type_custom VARCHAR(200),
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high')),
    is_standard BOOLEAN DEFAULT TRUE,
    text_content TEXT NOT NULL,
    embedding vector(1536),
    full_text_vector tsvector,
    position_in_contract INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE obligations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    clause_id INTEGER REFERENCES clauses(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    responsible_party_id INTEGER REFERENCES parties(id),
    beneficiary_party_id INTEGER REFERENCES parties(id),
    due_date DATE,
    penalty_description TEXT,
    is_high_impact BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rights (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    clause_id INTEGER REFERENCES clauses(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    holder_party_id INTEGER REFERENCES parties(id),
    condition_description TEXT,
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE term_definitions (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    clause_id INTEGER REFERENCES clauses(id) ON DELETE SET NULL,
    term_name VARCHAR(300) NOT NULL,
    definition_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contract_id, term_name)
);

CREATE TABLE conditions (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    description TEXT NOT NULL,
    trigger_event TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE monetary_values (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    clause_id INTEGER REFERENCES clauses(id) ON DELETE SET NULL,
    amount DECIMAL(20,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',  -- ISO currency codes (3 chars)
    value_type VARCHAR(200),
    context TEXT,
    multiple_of_fees DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE risks (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    clause_id INTEGER REFERENCES clauses(id) ON DELETE CASCADE,
    risk_type_id INTEGER REFERENCES risk_types(id),
    risk_type_custom VARCHAR(200),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    rationale TEXT,
    detected_by VARCHAR(50),
    is_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE extraction_jobs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    retry_count INTEGER DEFAULT 0,
    error_payload JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_contracts_tenant ON contracts(tenant_id);
CREATE INDEX idx_contracts_type ON contracts(contract_type);
CREATE INDEX idx_contracts_dates ON contracts(effective_date, expiration_date);
CREATE INDEX idx_contracts_risk ON contracts(risk_score_overall);
CREATE INDEX idx_contracts_reference ON contracts(reference_number);

CREATE INDEX idx_contract_relationships_child ON contract_relationships(child_contract_id);
CREATE INDEX idx_contract_relationships_parent ON contract_relationships(parent_contract_id);
CREATE INDEX idx_contract_relationships_type ON contract_relationships(relationship_type);
CREATE INDEX idx_contract_relationships_parent_ref ON contract_relationships(parent_reference_number);

CREATE INDEX idx_parties_tenant ON parties(tenant_id);
CREATE INDEX idx_parties_name ON parties(name);
CREATE INDEX idx_parties_canonical ON parties(canonical_name);
CREATE INDEX idx_parties_canonical_trgm ON parties USING gin(canonical_name gin_trgm_ops);  -- Trigram index for fuzzy matching

CREATE INDEX idx_clauses_contract ON clauses(contract_id);
CREATE INDEX idx_clauses_type ON clauses(clause_type_id);
CREATE INDEX idx_clauses_risk ON clauses(risk_level);
CREATE INDEX idx_clauses_fulltext ON clauses USING gin(full_text_vector);
CREATE INDEX idx_clauses_embedding ON clauses USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_obligations_clause ON obligations(clause_id);
CREATE INDEX idx_obligations_parties ON obligations(responsible_party_id, beneficiary_party_id);

CREATE INDEX idx_rights_clause ON rights(clause_id);
CREATE INDEX idx_rights_holder ON rights(holder_party_id);

CREATE INDEX idx_risks_contract ON risks(contract_id);
CREATE INDEX idx_risks_clause ON risks(clause_id);
CREATE INDEX idx_risks_level ON risks(risk_level);

-- Trigger for full-text search vector update
CREATE OR REPLACE FUNCTION update_clause_fulltext() RETURNS trigger AS $$
BEGIN
    NEW.full_text_vector := to_tsvector('english', 
        COALESCE(NEW.title, '') || ' ' || 
        COALESCE(NEW.text_content, '') || ' ' || 
        COALESCE(NEW.section_label, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_clauses_fulltext
    BEFORE INSERT OR UPDATE OF text_content, title, section_label ON clauses
    FOR EACH ROW EXECUTE FUNCTION update_clause_fulltext();

-- Insert lookup data
INSERT INTO clause_types (name, description) VALUES
    ('Definitions', 'Term definitions and interpretations'),
    ('Indemnification', 'Liability and indemnification clauses'),
    ('Limitation of Liability', 'Caps and limitations on liability'),
    ('Confidentiality', 'Confidential information protection'),
    ('Intellectual Property', 'IP ownership and licensing'),
    ('Termination', 'Contract termination conditions'),
    ('Payment Terms', 'Payment schedules and conditions'),
    ('Warranties', 'Representations and warranties'),
    ('Data Protection', 'Data privacy and security obligations'),
    ('Force Majeure', 'Unforeseeable circumstances provisions'),
    ('Dispute Resolution', 'Arbitration and dispute handling'),
    ('Service Level Agreement', 'SLA commitments and metrics'),
    ('Change Management', 'Procedures for contract modifications'),
    ('Acceptance Criteria', 'Deliverable acceptance terms'),
    ('Insurance', 'Insurance coverage requirements'),
    ('Other', 'Miscellaneous or uncategorized clauses');

INSERT INTO risk_types (name, description, severity_default) VALUES
    ('Uncapped Liability', 'No limit on liability exposure', 'high'),
    ('Unlimited Indemnity', 'Broad indemnification obligations', 'high'),
    ('Auto-Renewal', 'Automatic contract renewal provisions', 'medium'),
    ('Unilateral Modification', 'One party can modify terms', 'high'),
    ('Data Sovereignty', 'Data location and jurisdiction risks', 'medium'),
    ('Weak Termination Rights', 'Difficult to exit contract', 'medium'),
    ('Intellectual Property Transfer', 'Unfavorable IP ownership terms', 'high'),
    ('Broad NDA Scope', 'Overly broad confidentiality obligations', 'low'),
    ('Payment Terms', 'Unfavorable payment conditions', 'medium'),
    ('Regulatory Compliance', 'Compliance requirement gaps', 'high');

INSERT INTO party_roles (name, description) VALUES
    ('Client', 'The customer or buyer'),
    ('Vendor', 'The supplier or service provider'),
    ('Licensor', 'Entity granting a license'),
    ('Licensee', 'Entity receiving a license'),
    ('Consultant', 'Professional services provider'),
    ('Partner', 'Strategic partner or collaborator'),
    ('Employer', 'Employing entity'),
    ('Employee', 'Employed individual'),
    ('Landlord', 'Property owner in lease'),
    ('Tenant', 'Property renter in lease');
