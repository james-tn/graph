"""
Database-backed candidate parent generation.

Given a child contract row, query PostgreSQL for plausible parent candidates
using cheap pre-filters (party overlap, type compatibility, date ordering)
before handing the small candidate set to the XGBoost scorer.

The query joins through `parties_contracts` so we only retrieve contracts
that share at least one party with the child. This typically reduces the
candidate set from "every contract in the database" to ~5-50.
"""

from __future__ import annotations

from typing import Any, Optional

# Map child contract_type -> set of allowed parent contract_types.
# Mirrors VALID_HIERARCHY in feature_extractor.py but keyed the other way
# around so the SQL filter is direct.
ALLOWED_PARENT_TYPES_FOR_CHILD: dict[str, list[str]] = {
    "SOW": ["MSA", "Contract"],
    "Statement of Work": ["MSA", "Master Services Agreement", "Contract"],
    "Amendment": ["MSA", "SOW", "Contract", "Master Services Agreement"],
    "Addendum": ["MSA", "SOW", "Contract", "Master Services Agreement"],
    "WorkOrder": ["MSA", "SOW", "Master Services Agreement"],
    "Work Order": ["MSA", "SOW", "Master Services Agreement"],
    "Maintenance": ["MSA", "Contract", "Master Services Agreement"],
}


def allowed_parent_types(child_type: str) -> list[str]:
    """Return the list of contract_type strings that may parent this child."""
    if not child_type:
        return ["MSA", "Master Services Agreement", "Contract", "SOW"]
    # Direct match first, otherwise try a fuzzy fallback
    if child_type in ALLOWED_PARENT_TYPES_FOR_CHILD:
        return ALLOWED_PARENT_TYPES_FOR_CHILD[child_type]
    lowered = child_type.lower()
    if "amendment" in lowered:
        return ALLOWED_PARENT_TYPES_FOR_CHILD["Amendment"]
    if "statement of work" in lowered or lowered == "sow":
        return ALLOWED_PARENT_TYPES_FOR_CHILD["SOW"]
    if "addendum" in lowered:
        return ALLOWED_PARENT_TYPES_FOR_CHILD["Addendum"]
    if "work order" in lowered or "workorder" in lowered:
        return ALLOWED_PARENT_TYPES_FOR_CHILD["WorkOrder"]
    if "maintenance" in lowered:
        return ALLOWED_PARENT_TYPES_FOR_CHILD["Maintenance"]
    # Default: any plausible top-level container
    return ["MSA", "Master Services Agreement", "Contract", "SOW"]


def fetch_candidate_parents(
    cur,
    child_contract_id: int,
    child_contract_type: str,
    child_effective_date,
    tenant_id: str = "default",
    max_candidates: int = 50,
) -> list[dict]:
    """
    Return candidate parent contract dicts (one per row) for a child.

    Filters applied (cheap, in SQL):
      1. Same tenant
      2. Different contract id
      3. Shares at least one party with the child
      4. contract_type IN allowed_parent_types_for_child
      5. effective_date IS NULL OR effective_date <= child.effective_date
      6. Sorted most-recent-first, LIMIT max_candidates

    The returned dicts have the keys expected by feature_extractor.extract_features().
    """
    parent_types = allowed_parent_types(child_contract_type)

    # If we don't know the child's effective date, skip the date filter.
    date_filter_sql = ""
    params: list[Any] = []

    cur.execute(
        """
        WITH child_parties AS (
            SELECT party_id
            FROM parties_contracts
            WHERE contract_id = %s
        ),
        candidates AS (
            SELECT DISTINCT c.id
            FROM contracts c
            JOIN parties_contracts pc ON pc.contract_id = c.id
            WHERE c.tenant_id = %s
              AND c.id != %s
              AND pc.party_id IN (SELECT party_id FROM child_parties)
              AND c.contract_type = ANY(%s)
              AND (
                  %s::date IS NULL
                  OR c.effective_date IS NULL
                  OR c.effective_date <= %s::date
              )
        )
        SELECT
            c.id,
            c.contract_identifier,
            c.reference_number,
            c.title,
            c.contract_type,
            c.effective_date,
            c.expiration_date,
            c.governing_law,
            c.status,
            c.source_markdown AS full_text,
            COALESCE(
                (
                    SELECT json_agg(json_build_object(
                        'canonical_name', p.canonical_name,
                        'role', COALESCE(pr.name, pc.role_description)
                    ))
                    FROM parties_contracts pc
                    LEFT JOIN parties p ON p.id = pc.party_id
                    LEFT JOIN party_roles pr ON pr.id = pc.role_id
                    WHERE pc.contract_id = c.id
                ),
                '[]'::json
            ) AS parties,
            (
                SELECT mv.amount
                FROM monetary_values mv
                WHERE mv.contract_id = c.id
                  AND mv.value_type = 'Total Contract Value'
                ORDER BY mv.id ASC
                LIMIT 1
            ) AS total_value,
            (
                SELECT mv.currency
                FROM monetary_values mv
                WHERE mv.contract_id = c.id
                  AND mv.value_type = 'Total Contract Value'
                ORDER BY mv.id ASC
                LIMIT 1
            ) AS currency
        FROM contracts c
        WHERE c.id IN (SELECT id FROM candidates)
        ORDER BY c.effective_date DESC NULLS LAST
        LIMIT %s
        """,
        (
            child_contract_id,
            tenant_id,
            child_contract_id,
            parent_types,
            child_effective_date,
            child_effective_date,
            max_candidates,
        ),
    )
    rows = cur.fetchall()

    candidates: list[dict] = []
    for row in rows:
        # Convert RealDictRow to plain dict and normalize parties type
        d = dict(row)
        if d.get("parties") is None:
            d["parties"] = []
        candidates.append(d)
    return candidates


def fetch_child_contract_dict(
    cur,
    child_contract_id: int,
    extracted_parent_reference: Optional[str] = None,
) -> dict:
    """Fetch a child contract row in the same shape as fetch_candidate_parents() returns."""
    cur.execute(
        """
        SELECT
            c.id,
            c.contract_identifier,
            c.reference_number,
            c.title,
            c.contract_type,
            c.effective_date,
            c.expiration_date,
            c.governing_law,
            c.status,
            c.source_markdown AS full_text,
            COALESCE(
                (
                    SELECT json_agg(json_build_object(
                        'canonical_name', p.canonical_name,
                        'role', COALESCE(pr.name, pc.role_description)
                    ))
                    FROM parties_contracts pc
                    LEFT JOIN parties p ON p.id = pc.party_id
                    LEFT JOIN party_roles pr ON pr.id = pc.role_id
                    WHERE pc.contract_id = c.id
                ),
                '[]'::json
            ) AS parties,
            (
                SELECT mv.amount
                FROM monetary_values mv
                WHERE mv.contract_id = c.id
                  AND mv.value_type = 'Total Contract Value'
                LIMIT 1
            ) AS total_value,
            (
                SELECT mv.currency
                FROM monetary_values mv
                WHERE mv.contract_id = c.id
                  AND mv.value_type = 'Total Contract Value'
                LIMIT 1
            ) AS currency
        FROM contracts c
        WHERE c.id = %s
        """,
        (child_contract_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"Contract {child_contract_id} not found")
    d = dict(row)
    if d.get("parties") is None:
        d["parties"] = []
    d["extracted_parent_reference"] = extracted_parent_reference
    return d
