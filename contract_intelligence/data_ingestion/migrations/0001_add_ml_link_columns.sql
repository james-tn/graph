-- Migration: add ML-assisted hierarchy linking columns + review queue
--
-- Forward-only migration. Idempotent: uses IF NOT EXISTS / IF EXISTS guards.
-- Run against an existing schema before deploying the ML-linker code.
--
-- Usage:
--   psql -h $POSTGRES_HOST -d $POSTGRES_DATABASE -U $POSTGRES_USER \
--        -f data_ingestion/migrations/0001_add_ml_link_columns.sql

BEGIN;

-- 1. Add audit columns to contract_relationships
ALTER TABLE contract_relationships
    ADD COLUMN IF NOT EXISTS link_method VARCHAR(30) NOT NULL DEFAULT 'rule_based',
    ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(5,4),
    ADD COLUMN IF NOT EXISTS model_version VARCHAR(50),
    ADD COLUMN IF NOT EXISTS top_features JSONB,
    ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(200),
    ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_contract_rel_method
    ON contract_relationships(link_method);

-- 2. Create link_review_queue table
CREATE TABLE IF NOT EXISTS link_review_queue (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'default',
    child_contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    candidate_parent_id INTEGER REFERENCES contracts(id) ON DELETE SET NULL,
    relationship_type VARCHAR(50),
    extracted_parent_reference VARCHAR(200),
    confidence_score NUMERIC(5,4),
    model_version VARCHAR(50),
    top_features JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    reviewed_by VARCHAR(200),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_link_review_queue_status
    ON link_review_queue(status);
CREATE INDEX IF NOT EXISTS idx_link_review_queue_child
    ON link_review_queue(child_contract_id);

-- 3. Backfill: existing rows came from the rule-based linker, so set their
--    link_method explicitly (the DEFAULT only applies to new inserts).
UPDATE contract_relationships
SET link_method = 'rule_based'
WHERE link_method IS NULL OR link_method = '';

COMMIT;
