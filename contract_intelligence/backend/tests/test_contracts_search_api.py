"""
Unit tests for the contracts search FastAPI route.

Mocks `backend.app.api.contracts_search.get_connection` with a tiny in-memory
fake psycopg2 connection. Auth is disabled via DISABLE_AUTH=true.
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pytest

# Ensure the contract_intelligence/ root is importable.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DISABLE_AUTH", "true")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.app.api import contracts_search as cs_module  # noqa: E402


# ---------------------------------------------------------------------------
# Fake connection
# ---------------------------------------------------------------------------


class FakeCursor:
    def __init__(self, contracts: list[dict]):
        self.contracts = contracts
        self._rows: list[dict] = []
        self._index = 0
        self.last_sql = ""
        self.last_params: tuple = ()

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def execute(self, sql: str, params: Any = None):
        self.last_sql = sql
        self.last_params = tuple(params) if params else ()
        # The endpoint passes params in this order:
        #   pattern, pattern, prefix_pattern, pattern, pattern, pattern, pattern,
        #   [contract_type,] limit
        # We extract the user query from the first %X% pattern.
        first_pattern = self.last_params[0] if self.last_params else ""
        q = first_pattern.strip("%").lower() if isinstance(first_pattern, str) else ""

        # Optional contract_type filter (one extra param BEFORE limit).
        # If we see 9 params, [-2] is the type filter; if 8, no filter.
        type_filter = None
        if len(self.last_params) >= 9:
            type_filter = self.last_params[-2]

        limit = self.last_params[-1] if self.last_params else 20

        scored: list[dict] = []
        for c in self.contracts:
            ref = (c.get("reference_number") or "").lower()
            ident = (c.get("contract_identifier") or "").lower()
            title = (c.get("title") or "").lower()
            if q and q not in ref and q not in ident and q not in title:
                continue
            if type_filter is not None and c.get("contract_type") != type_filter:
                continue
            score = 0.0
            if q in ref:
                score += 3.0
            if q in ident:
                score += 3.0
            if title.startswith(q):
                score += 2.0
            if q in title:
                score += 1.0
            row = dict(c)
            row["score"] = score
            scored.append(row)

        scored.sort(key=lambda r: (-r["score"], r.get("contract_identifier") or ""))
        self._rows = scored[:limit]
        self._index = 0

    def fetchall(self):
        rows = self._rows[self._index:]
        self._index = len(self._rows)
        return rows

    def fetchone(self):
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return row

    def close(self):
        pass


class FakeConn:
    def __init__(self, contracts: list[dict]):
        self.contracts = contracts

    def cursor(self):
        return FakeCursor(self.contracts)

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def contracts():
    return [
        {
            "id": 100,
            "contract_identifier": "MSA-001",
            "reference_number": "MSA-ZEN-202403-197",
            "title": "Master Services Agreement with Zenith",
            "contract_type": "MSA",
            "effective_date": date(2024, 3, 1),
            "expiration_date": date(2027, 3, 1),
        },
        {
            "id": 101,
            "contract_identifier": "MSA-002",
            "reference_number": "MSA-ACME-202401-050",
            "title": "Acme MSA",
            "contract_type": "MSA",
            "effective_date": date(2024, 1, 1),
            "expiration_date": date(2027, 1, 1),
        },
        {
            "id": 200,
            "contract_identifier": "SOW-001",
            "reference_number": "SOW-ZEN-202403-200",
            "title": "Statement of Work — Zenith Phase 1",
            "contract_type": "SOW",
            "effective_date": date(2024, 4, 1),
            "expiration_date": date(2025, 4, 1),
        },
        {
            "id": 201,
            "contract_identifier": "AMD-001",
            "reference_number": "AMD-ZEN-202403-201",
            "title": "Amendment to Zenith MSA",
            "contract_type": "Amendment",
            "effective_date": date(2024, 5, 1),
            "expiration_date": None,
        },
    ]


@pytest.fixture
def client(contracts, monkeypatch):
    monkeypatch.setattr(cs_module, "get_connection", lambda: FakeConn(contracts))
    app = FastAPI()
    app.include_router(cs_module.router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_search_by_reference_number(client):
    resp = client.get("/api/contracts/search", params={"q": "MSA-ZEN-202403-197"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert body["items"][0]["id"] == 100
    assert body["items"][0]["score"] >= 3.0


def test_search_partial_reference(client):
    resp = client.get("/api/contracts/search", params={"q": "ZEN-202403"})
    assert resp.status_code == 200
    body = resp.json()
    ids = {hit["id"] for hit in body["items"]}
    # All three Zenith contracts should match.
    assert {100, 200, 201}.issubset(ids)


def test_search_by_title(client):
    resp = client.get("/api/contracts/search", params={"q": "Statement of Work"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert body["items"][0]["id"] == 200


def test_search_by_identifier(client):
    resp = client.get("/api/contracts/search", params={"q": "MSA-001"})
    assert resp.status_code == 200
    body = resp.json()
    ids = [hit["id"] for hit in body["items"]]
    assert 100 in ids


def test_filter_by_contract_type(client):
    resp = client.get(
        "/api/contracts/search",
        params={"q": "ZEN", "contract_type": "Amendment"},
    )
    assert resp.status_code == 200
    body = resp.json()
    types = {hit["contract_type"] for hit in body["items"]}
    assert types == {"Amendment"}
    assert all(hit["id"] == 201 for hit in body["items"])


def test_limit_respected(client):
    resp = client.get("/api/contracts/search", params={"q": "ZEN", "limit": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_results_sorted_by_score(client):
    resp = client.get("/api/contracts/search", params={"q": "Zenith"})
    assert resp.status_code == 200
    body = resp.json()
    scores = [hit["score"] for hit in body["items"]]
    assert scores == sorted(scores, reverse=True)


def test_dates_iso_serialized(client):
    resp = client.get("/api/contracts/search", params={"q": "MSA-ZEN-202403-197"})
    assert resp.status_code == 200
    hit = resp.json()["items"][0]
    assert hit["effective_date"].startswith("2024-03-01")
    assert hit["expiration_date"].startswith("2027-03-01")


def test_empty_query_rejected(client):
    resp = client.get("/api/contracts/search", params={"q": "   "})
    # Pydantic min_length=1 rejects empty (after stripping in handler we 400)
    # FastAPI itself sees length==3 (spaces), so we hit the .strip() guard.
    assert resp.status_code == 400


def test_no_match_returns_empty(client):
    resp = client.get("/api/contracts/search", params={"q": "NOMATCHXYZZY"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []
