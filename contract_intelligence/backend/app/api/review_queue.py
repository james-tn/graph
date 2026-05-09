"""
Review queue API for the ML hierarchy linker.

When the linker assigns a parent with confidence in the [REVIEW, AUTO) band,
a row is added to `link_review_queue` instead of creating a relationship.
This module exposes endpoints for a human reviewer to inspect and decide.

Endpoints (mounted under /api/review-queue in main.py):
    GET    /                      list pending items (paged, filterable by status)
    GET    /stats                 counts by status (for UI badges)
    GET    /{review_id}           full detail for one item, including the candidate
                                  contract and the child contract context
    POST   /{review_id}/decide    apply a decision: confirm | reject | relink

A "confirm" creates a contract_relationships row with link_method='ml_review_confirmed'.
A "reject" only flags the queue entry; it does NOT create a relationship. The pair
becomes a labeled negative for the next retraining run.
A "relink" lets the reviewer pick a different parent_contract_id; we record the
relationship with link_method='manual' and mark the queue row as 'relinked'.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

try:
    # Auth dependency: optional in dev (DISABLE_AUTH=true). Routes accept Optional[dict].
    from backend.app.core.auth import get_current_user, get_user_email
except Exception:  # pragma: no cover - import-time failure shouldn't kill the API
    get_current_user = lambda: None  # type: ignore[assignment]

    def get_user_email(_user):  # type: ignore[no-redef]
        return None

from backend.app.core.db import get_connection


router = APIRouter(prefix="/api/review-queue", tags=["review-queue"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ContractSummary(BaseModel):
    id: int
    contract_identifier: Optional[str] = None
    reference_number: Optional[str] = None
    title: Optional[str] = None
    contract_type: Optional[str] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None


class FeatureContribution(BaseModel):
    feature: str
    contribution: float


class ReviewItem(BaseModel):
    model_config = {"protected_namespaces": ()}

    id: int
    status: str
    confidence_score: Optional[float] = None
    model_version: Optional[str] = None
    relationship_type: Optional[str] = None
    extracted_parent_reference: Optional[str] = None
    created_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_notes: Optional[str] = None
    child: ContractSummary
    candidate_parent: Optional[ContractSummary] = None
    top_features: list[FeatureContribution] = Field(default_factory=list)


class ReviewListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ReviewItem]


class ReviewStatsResponse(BaseModel):
    pending: int
    confirmed: int
    rejected: int
    relinked: int
    total: int


class DecideRequest(BaseModel):
    action: Literal["confirm", "reject", "relink"]
    new_parent_contract_id: Optional[int] = None  # required for "relink"
    notes: Optional[str] = None


class DecideResponse(BaseModel):
    review_id: int
    status: str
    relationship_id: Optional[int] = None
    message: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_CONTRACT_FIELDS = (
    "id",
    "contract_identifier",
    "reference_number",
    "title",
    "contract_type",
    "effective_date",
    "expiration_date",
)


def _row_to_contract(row: dict | None) -> ContractSummary | None:
    if not row:
        return None
    payload = {k: row.get(k) for k in _CONTRACT_FIELDS}
    # Dates -> ISO strings for JSON
    for date_key in ("effective_date", "expiration_date"):
        v = payload.get(date_key)
        if isinstance(v, datetime) or hasattr(v, "isoformat"):
            payload[date_key] = v.isoformat() if v else None
    return ContractSummary(**payload)


def _parse_top_features(raw: Any) -> list[FeatureContribution]:
    if raw is None:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []
    if not isinstance(raw, list):
        return []
    out: list[FeatureContribution] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        feat = item.get("feature")
        contrib = item.get("contribution")
        if feat is None or contrib is None:
            continue
        try:
            out.append(FeatureContribution(feature=str(feat), contribution=float(contrib)))
        except (TypeError, ValueError):
            continue
    return out


def _row_to_review_item(
    queue_row: dict,
    child_row: dict | None,
    candidate_row: dict | None,
) -> ReviewItem:
    return ReviewItem(
        id=queue_row["id"],
        status=queue_row["status"],
        confidence_score=(
            float(queue_row["confidence_score"])
            if queue_row.get("confidence_score") is not None
            else None
        ),
        model_version=queue_row.get("model_version"),
        relationship_type=queue_row.get("relationship_type"),
        extracted_parent_reference=queue_row.get("extracted_parent_reference"),
        created_at=(
            queue_row["created_at"].isoformat()
            if queue_row.get("created_at")
            else None
        ),
        reviewed_by=queue_row.get("reviewed_by"),
        reviewed_at=(
            queue_row["reviewed_at"].isoformat()
            if queue_row.get("reviewed_at")
            else None
        ),
        review_notes=queue_row.get("review_notes"),
        child=_row_to_contract(child_row) or ContractSummary(id=queue_row["child_contract_id"]),
        candidate_parent=_row_to_contract(candidate_row),
        top_features=_parse_top_features(queue_row.get("top_features")),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/stats", response_model=ReviewStatsResponse)
async def review_queue_stats(user: Optional[dict] = Depends(get_current_user)):
    """Return counts of queue rows by status."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM link_review_queue
                GROUP BY status
                """
            )
            counts = {row["status"]: int(row["count"]) for row in cur.fetchall()}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Stats query failed: {exc}")
    finally:
        conn.close()

    pending = counts.get("pending", 0)
    confirmed = counts.get("confirmed", 0)
    rejected = counts.get("rejected", 0)
    relinked = counts.get("relinked", 0)
    return ReviewStatsResponse(
        pending=pending,
        confirmed=confirmed,
        rejected=rejected,
        relinked=relinked,
        total=pending + confirmed + rejected + relinked,
    )


@router.get("", response_model=ReviewListResponse)
async def list_review_items(
    status: str = Query("pending", description="pending | confirmed | rejected | relinked | all"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: Literal["confidence_desc", "confidence_asc", "newest", "oldest"] = "confidence_desc",
    user: Optional[dict] = Depends(get_current_user),
):
    """List review queue items with paging and basic filtering."""
    valid_statuses = {"pending", "confirmed", "rejected", "relinked", "all"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}.")

    sort_clause = {
        "confidence_desc": "q.confidence_score DESC NULLS LAST, q.id DESC",
        "confidence_asc": "q.confidence_score ASC NULLS LAST, q.id DESC",
        "newest": "q.created_at DESC, q.id DESC",
        "oldest": "q.created_at ASC, q.id ASC",
    }[sort]

    where_clause = "" if status == "all" else "WHERE q.status = %s"
    params: list[Any] = [] if status == "all" else [status]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # total count for paging
            count_sql = f"SELECT COUNT(*) AS total FROM link_review_queue q {where_clause}"
            cur.execute(count_sql, params)
            total = int(cur.fetchone()["total"])

            list_sql = f"""
                SELECT
                    q.id,
                    q.status,
                    q.confidence_score,
                    q.model_version,
                    q.relationship_type,
                    q.extracted_parent_reference,
                    q.top_features,
                    q.child_contract_id,
                    q.candidate_parent_id,
                    q.created_at,
                    q.reviewed_by,
                    q.reviewed_at,
                    q.review_notes,
                    c.id              AS c_id,
                    c.contract_identifier AS c_contract_identifier,
                    c.reference_number    AS c_reference_number,
                    c.title               AS c_title,
                    c.contract_type       AS c_contract_type,
                    c.effective_date      AS c_effective_date,
                    c.expiration_date     AS c_expiration_date,
                    p.id              AS p_id,
                    p.contract_identifier AS p_contract_identifier,
                    p.reference_number    AS p_reference_number,
                    p.title               AS p_title,
                    p.contract_type       AS p_contract_type,
                    p.effective_date      AS p_effective_date,
                    p.expiration_date     AS p_expiration_date
                FROM link_review_queue q
                LEFT JOIN contracts c ON c.id = q.child_contract_id
                LEFT JOIN contracts p ON p.id = q.candidate_parent_id
                {where_clause}
                ORDER BY {sort_clause}
                LIMIT %s OFFSET %s
            """
            cur.execute(list_sql, [*params, limit, offset])
            rows = cur.fetchall()

        items: list[ReviewItem] = []
        for row in rows:
            child_row = {
                "id": row["c_id"],
                "contract_identifier": row["c_contract_identifier"],
                "reference_number": row["c_reference_number"],
                "title": row["c_title"],
                "contract_type": row["c_contract_type"],
                "effective_date": row["c_effective_date"],
                "expiration_date": row["c_expiration_date"],
            } if row["c_id"] is not None else None
            candidate_row = {
                "id": row["p_id"],
                "contract_identifier": row["p_contract_identifier"],
                "reference_number": row["p_reference_number"],
                "title": row["p_title"],
                "contract_type": row["p_contract_type"],
                "effective_date": row["p_effective_date"],
                "expiration_date": row["p_expiration_date"],
            } if row["p_id"] is not None else None
            items.append(_row_to_review_item(row, child_row, candidate_row))

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"List query failed: {exc}")
    finally:
        conn.close()

    return ReviewListResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{review_id}", response_model=ReviewItem)
async def get_review_item(review_id: int, user: Optional[dict] = Depends(get_current_user)):
    """Return full detail for one queue item."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    q.id, q.status, q.confidence_score, q.model_version,
                    q.relationship_type, q.extracted_parent_reference,
                    q.top_features, q.child_contract_id, q.candidate_parent_id,
                    q.created_at, q.reviewed_by, q.reviewed_at, q.review_notes
                FROM link_review_queue q
                WHERE q.id = %s
                """,
                (review_id,),
            )
            queue_row = cur.fetchone()
            if not queue_row:
                raise HTTPException(status_code=404, detail=f"Review item {review_id} not found")

            child_row = _fetch_contract(cur, queue_row["child_contract_id"])
            candidate_row = (
                _fetch_contract(cur, queue_row["candidate_parent_id"])
                if queue_row["candidate_parent_id"]
                else None
            )
        return _row_to_review_item(queue_row, child_row, candidate_row)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Detail query failed: {exc}")
    finally:
        conn.close()


@router.post("/{review_id}/decide", response_model=DecideResponse)
async def decide_review_item(
    review_id: int,
    body: DecideRequest,
    user: Optional[dict] = Depends(get_current_user),
):
    """Apply a reviewer decision to a queue item.

    - confirm: creates the relationship with link_method='ml_review_confirmed'
    - reject:  marks the row as rejected; no relationship is created
    - relink:  creates a relationship to a different parent (link_method='manual')
    """
    reviewer = get_user_email(user) or os.environ.get("REVIEWER_EMAIL_OVERRIDE") or "system"

    if body.action == "relink" and not body.new_parent_contract_id:
        raise HTTPException(status_code=400, detail="new_parent_contract_id is required for relink")

    conn = get_connection()
    try:
        with conn:  # transaction
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, status, child_contract_id, candidate_parent_id,
                           relationship_type, confidence_score, model_version,
                           top_features, extracted_parent_reference, tenant_id
                    FROM link_review_queue
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (review_id,),
                )
                queue_row = cur.fetchone()
                if not queue_row:
                    raise HTTPException(status_code=404, detail=f"Review item {review_id} not found")
                if queue_row["status"] != "pending":
                    raise HTTPException(
                        status_code=409,
                        detail=f"Review item {review_id} already decided (status={queue_row['status']})",
                    )

                relationship_id: Optional[int] = None
                new_status: str

                if body.action == "confirm":
                    if not queue_row["candidate_parent_id"]:
                        raise HTTPException(
                            status_code=400,
                            detail="Cannot confirm: queue row has no candidate_parent_id",
                        )
                    relationship_id = _insert_relationship(
                        cur,
                        tenant_id=queue_row.get("tenant_id") or "default",
                        child_id=queue_row["child_contract_id"],
                        parent_id=queue_row["candidate_parent_id"],
                        parent_reference=queue_row["extracted_parent_reference"],
                        relationship_type=queue_row["relationship_type"] or "related",
                        link_method="ml_review_confirmed",
                        confidence=queue_row["confidence_score"],
                        model_version=queue_row["model_version"],
                        top_features=queue_row["top_features"],
                        reviewed_by=reviewer,
                    )
                    new_status = "confirmed"

                elif body.action == "relink":
                    relationship_id = _insert_relationship(
                        cur,
                        tenant_id=queue_row.get("tenant_id") or "default",
                        child_id=queue_row["child_contract_id"],
                        parent_id=body.new_parent_contract_id,
                        parent_reference=queue_row["extracted_parent_reference"],
                        relationship_type=queue_row["relationship_type"] or "related",
                        link_method="manual",
                        confidence=None,
                        model_version=queue_row["model_version"],
                        top_features=None,
                        reviewed_by=reviewer,
                    )
                    new_status = "relinked"

                else:  # reject
                    new_status = "rejected"

                cur.execute(
                    """
                    UPDATE link_review_queue
                    SET status = %s,
                        reviewed_by = %s,
                        reviewed_at = CURRENT_TIMESTAMP,
                        review_notes = COALESCE(%s, review_notes)
                    WHERE id = %s
                    """,
                    (new_status, reviewer, body.notes, review_id),
                )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Decision failed: {exc}")
    finally:
        conn.close()

    return DecideResponse(
        review_id=review_id,
        status=new_status,
        relationship_id=relationship_id,
        message=f"Review item {review_id} marked {new_status} by {reviewer}",
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _fetch_contract(cur, contract_id: int) -> dict | None:
    cur.execute(
        """
        SELECT id, contract_identifier, reference_number, title,
               contract_type, effective_date, expiration_date
        FROM contracts
        WHERE id = %s
        """,
        (contract_id,),
    )
    return cur.fetchone()


def _insert_relationship(
    cur,
    *,
    tenant_id: str,
    child_id: int,
    parent_id: int,
    parent_reference: Optional[str],
    relationship_type: str,
    link_method: str,
    confidence: Optional[float],
    model_version: Optional[str],
    top_features: Any,
    reviewed_by: str,
) -> Optional[int]:
    """Insert (or upsert) a contract_relationships row, return its id."""
    # Normalize top_features for JSONB insert
    if top_features is None:
        top_features_json = None
    elif isinstance(top_features, str):
        top_features_json = top_features
    else:
        top_features_json = json.dumps(top_features)

    cur.execute(
        """
        INSERT INTO contract_relationships (
            tenant_id,
            child_contract_id,
            parent_contract_id,
            parent_reference_number,
            relationship_type,
            link_method,
            confidence_score,
            model_version,
            top_features,
            reviewed_by,
            reviewed_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (child_contract_id, parent_contract_id, relationship_type)
        DO UPDATE SET
            link_method = EXCLUDED.link_method,
            confidence_score = COALESCE(EXCLUDED.confidence_score, contract_relationships.confidence_score),
            model_version = COALESCE(EXCLUDED.model_version, contract_relationships.model_version),
            top_features = COALESCE(EXCLUDED.top_features, contract_relationships.top_features),
            reviewed_by = EXCLUDED.reviewed_by,
            reviewed_at = EXCLUDED.reviewed_at
        RETURNING id
        """,
        (
            tenant_id,
            child_id,
            parent_id,
            parent_reference,
            relationship_type,
            link_method,
            confidence,
            model_version,
            top_features_json,
            reviewed_by,
        ),
    )
    row = cur.fetchone()
    return int(row["id"]) if row else None
