"""
Lightweight contracts search API used by the Review Queue UI to drive a
"relink to a different parent" picker.

Endpoint:
    GET /api/contracts/search?q=<query>&limit=20

Returns up to `limit` contracts matched by:
    - reference_number ILIKE '%q%'  (boosted)
    - contract_identifier ILIKE '%q%' (boosted)
    - title ILIKE '%q%'

Why a separate endpoint instead of reusing the agent search:
    - The reviewer needs a *deterministic*, instant lookup by reference/title.
    - The hybrid search agent is much heavier (LLM + vectors) and can return
      hallucinated answers. For relinking we want a small JSON list of real
      candidate contracts ranked by simple textual relevance.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

try:
    from backend.app.core.auth import get_current_user
except Exception:  # pragma: no cover
    get_current_user = lambda: None  # type: ignore[assignment]

from backend.app.core.db import get_connection


router = APIRouter(prefix="/api/contracts", tags=["contracts"])


class ContractSearchHit(BaseModel):
    id: int
    contract_identifier: Optional[str] = None
    reference_number: Optional[str] = None
    title: Optional[str] = None
    contract_type: Optional[str] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    score: float


class ContractSearchResponse(BaseModel):
    query: str
    total: int
    items: list[ContractSearchHit]


def _iso(value):
    if value is None:
        return None
    if isinstance(value, datetime) or hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


@router.get("/search", response_model=ContractSearchResponse)
async def search_contracts(
    q: str = Query(..., min_length=1, max_length=200, description="Free-text query"),
    limit: int = Query(20, ge=1, le=100),
    contract_type: Optional[str] = Query(
        None, description="Optional filter: only return contracts of this type"
    ),
    user: Optional[dict] = Depends(get_current_user),
):
    """Match `q` against reference_number, contract_identifier, and title.

    The relevance score is computed in SQL:
        +3.0 if reference_number ILIKE %q%
        +3.0 if contract_identifier ILIKE %q%
        +2.0 if title ILIKE %q% from the start (prefix-style)
        +1.0 if title ILIKE %q% (anywhere)
    """
    query_text = q.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    pattern = f"%{query_text}%"
    prefix_pattern = f"{query_text}%"

    sql = """
        SELECT
            id,
            contract_identifier,
            reference_number,
            title,
            contract_type,
            effective_date,
            expiration_date,
            (
                CASE WHEN reference_number ILIKE %s THEN 3.0 ELSE 0.0 END +
                CASE WHEN contract_identifier ILIKE %s THEN 3.0 ELSE 0.0 END +
                CASE WHEN title ILIKE %s THEN 2.0 ELSE 0.0 END +
                CASE WHEN title ILIKE %s THEN 1.0 ELSE 0.0 END
            ) AS score
        FROM contracts
        WHERE (
            reference_number ILIKE %s
            OR contract_identifier ILIKE %s
            OR title ILIKE %s
        )
    """
    params: list = [
        pattern,           # ref exact-ish
        pattern,           # identifier exact-ish
        prefix_pattern,    # title prefix
        pattern,           # title anywhere
        pattern,
        pattern,
        pattern,
    ]
    if contract_type:
        sql += " AND contract_type = %s"
        params.append(contract_type)

    sql += " ORDER BY score DESC, contract_identifier ASC LIMIT %s"
    params.append(limit)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}")
    finally:
        conn.close()

    items = [
        ContractSearchHit(
            id=int(row["id"]),
            contract_identifier=row.get("contract_identifier"),
            reference_number=row.get("reference_number"),
            title=row.get("title"),
            contract_type=row.get("contract_type"),
            effective_date=_iso(row.get("effective_date")),
            expiration_date=_iso(row.get("expiration_date")),
            score=float(row.get("score") or 0.0),
        )
        for row in rows
    ]
    return ContractSearchResponse(query=query_text, total=len(items), items=items)
