"""
Unit tests for the review queue FastAPI routes.

Mocks `backend.app.api.review_queue.get_connection` with an in-memory fake
psycopg2 connection. Auth is disabled via DISABLE_AUTH=true so the auth
dependency short-circuits.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pytest

# Ensure the contract_intelligence/ root is importable for `backend.*` modules.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Disable auth before main is imported.
os.environ.setdefault("DISABLE_AUTH", "true")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.api import review_queue as rq_module  # noqa: E402


# ---------------------------------------------------------------------------
# Fake psycopg2 connection
# ---------------------------------------------------------------------------


class FakeCursor:
    """Tiny subset of psycopg2.extras.RealDictCursor.

    The real handler runs:
        SELECT status, COUNT(*) FROM link_review_queue GROUP BY status
        SELECT COUNT(*) AS total ...
        SELECT q.id, q.status, ... FROM link_review_queue q LEFT JOIN contracts ...
        SELECT q.id, q.status, ... FROM link_review_queue q WHERE q.id = %s
        SELECT id, contract_identifier, ... FROM contracts WHERE id = %s
        SELECT id, status, ... FROM link_review_queue WHERE id = %s FOR UPDATE
        UPDATE link_review_queue SET status = ...
        INSERT INTO contract_relationships ... RETURNING id
    """

    def __init__(self, store: "FakeStore"):
        self.store = store
        self._rows: list[dict] = []
        self._index = 0
        self.last_sql: str = ""
        self.last_params: tuple = ()

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def execute(self, sql: str, params: Any = None):
        self.last_sql = sql
        self.last_params = tuple(params) if params else ()
        s = sql.lower()
        if "select status, count(*)" in s and "link_review_queue" in s:
            counts: dict[str, int] = {}
            for row in self.store.queue.values():
                counts[row["status"]] = counts.get(row["status"], 0) + 1
            self._rows = [{"status": k, "count": v} for k, v in counts.items()]

        elif "count(*) as total" in s and "link_review_queue" in s:
            target_status = self.last_params[0] if self.last_params else None
            rows = [r for r in self.store.queue.values()
                    if target_status is None or r["status"] == target_status]
            self._rows = [{"total": len(rows)}]

        elif "from link_review_queue q" in s and "left join contracts c" in s:
            target_status = None
            if "where q.status" in s and self.last_params:
                target_status = self.last_params[0]
            limit = self.last_params[-2] if len(self.last_params) >= 2 else 50
            offset = self.last_params[-1] if self.last_params else 0
            rows = [r for r in self.store.queue.values()
                    if target_status is None or r["status"] == target_status]
            rows.sort(key=lambda r: (r.get("confidence_score") or 0.0), reverse=True)
            self._rows = [self._join_for_list(r) for r in rows[offset:offset + limit]]

        elif "from link_review_queue q" in s and "where q.id" in s:
            qid = int(self.last_params[0])
            row = self.store.queue.get(qid)
            self._rows = [self._serialize_queue_row(row)] if row else []

        elif s.strip().startswith("select id, contract_identifier"):
            cid = int(self.last_params[0])
            self._rows = [self.store.contracts[cid]] if cid in self.store.contracts else []

        elif "from link_review_queue" in s and "for update" in s:
            qid = int(self.last_params[0])
            row = self.store.queue.get(qid)
            self._rows = [self._serialize_queue_row(row)] if row else []

        elif s.strip().startswith("update link_review_queue"):
            new_status, reviewer, notes, qid = self.last_params
            row = self.store.queue.get(int(qid))
            if row is not None:
                row["status"] = new_status
                row["reviewed_by"] = reviewer
                row["reviewed_at"] = datetime.utcnow()
                if notes:
                    row["review_notes"] = notes
            self._rows = []

        elif s.strip().startswith("insert into contract_relationships"):
            (tenant_id, child_id, parent_id, parent_ref, rel_type, link_method,
             confidence, model_version, top_features_json, reviewed_by) = self.last_params
            new_id = self.store.next_relationship_id
            self.store.next_relationship_id += 1
            self.store.relationships[new_id] = {
                "id": new_id,
                "tenant_id": tenant_id,
                "child_contract_id": child_id,
                "parent_contract_id": parent_id,
                "parent_reference_number": parent_ref,
                "relationship_type": rel_type,
                "link_method": link_method,
                "confidence_score": confidence,
                "model_version": model_version,
                "top_features": top_features_json,
                "reviewed_by": reviewed_by,
            }
            self._rows = [{"id": new_id}]

        else:
            self._rows = []

        self._index = 0

    # --- result fetchers ----------------------------------------------------
    def fetchone(self):
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return row

    def fetchall(self):
        rows = self._rows[self._index:]
        self._index = len(self._rows)
        return rows

    def close(self):
        pass

    # --- helpers ------------------------------------------------------------
    def _serialize_queue_row(self, row: dict) -> dict:
        return {
            "id": row["id"],
            "status": row["status"],
            "confidence_score": row.get("confidence_score"),
            "model_version": row.get("model_version"),
            "relationship_type": row.get("relationship_type"),
            "extracted_parent_reference": row.get("extracted_parent_reference"),
            "top_features": row.get("top_features"),
            "child_contract_id": row.get("child_contract_id"),
            "candidate_parent_id": row.get("candidate_parent_id"),
            "created_at": row.get("created_at"),
            "reviewed_by": row.get("reviewed_by"),
            "reviewed_at": row.get("reviewed_at"),
            "review_notes": row.get("review_notes"),
            "tenant_id": row.get("tenant_id", "default"),
        }

    def _join_for_list(self, row: dict) -> dict:
        base = self._serialize_queue_row(row)
        child = self.store.contracts.get(row["child_contract_id"])
        parent = self.store.contracts.get(row.get("candidate_parent_id")) if row.get("candidate_parent_id") else None
        if child:
            base.update({
                "c_id": child["id"],
                "c_contract_identifier": child.get("contract_identifier"),
                "c_reference_number": child.get("reference_number"),
                "c_title": child.get("title"),
                "c_contract_type": child.get("contract_type"),
                "c_effective_date": child.get("effective_date"),
                "c_expiration_date": child.get("expiration_date"),
            })
        else:
            base.update({k: None for k in (
                "c_id", "c_contract_identifier", "c_reference_number",
                "c_title", "c_contract_type", "c_effective_date", "c_expiration_date",
            )})
        if parent:
            base.update({
                "p_id": parent["id"],
                "p_contract_identifier": parent.get("contract_identifier"),
                "p_reference_number": parent.get("reference_number"),
                "p_title": parent.get("title"),
                "p_contract_type": parent.get("contract_type"),
                "p_effective_date": parent.get("effective_date"),
                "p_expiration_date": parent.get("expiration_date"),
            })
        else:
            base.update({k: None for k in (
                "p_id", "p_contract_identifier", "p_reference_number",
                "p_title", "p_contract_type", "p_effective_date", "p_expiration_date",
            )})
        return base


class FakeConn:
    def __init__(self, store: "FakeStore"):
        self.store = store

    def cursor(self):
        return FakeCursor(self.store)

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


class FakeStore:
    def __init__(self):
        self.contracts: dict[int, dict] = {}
        self.queue: dict[int, dict] = {}
        self.relationships: dict[int, dict] = {}
        self.next_relationship_id = 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store(monkeypatch):
    s = FakeStore()
    s.contracts[100] = {
        "id": 100,
        "contract_identifier": "CHILD-1",
        "reference_number": "AMD-001",
        "title": "Amendment to MSA",
        "contract_type": "Amendment",
        "effective_date": date(2024, 6, 1),
        "expiration_date": date(2025, 6, 1),
    }
    s.contracts[200] = {
        "id": 200,
        "contract_identifier": "PARENT-1",
        "reference_number": "MSA-001",
        "title": "Master Services Agreement",
        "contract_type": "MSA",
        "effective_date": date(2023, 1, 1),
        "expiration_date": date(2026, 1, 1),
    }
    s.contracts[300] = {
        "id": 300,
        "contract_identifier": "PARENT-2",
        "reference_number": "MSA-002",
        "title": "Alternate MSA",
        "contract_type": "MSA",
        "effective_date": date(2023, 6, 1),
        "expiration_date": date(2026, 6, 1),
    }
    s.queue[1] = {
        "id": 1,
        "tenant_id": "default",
        "child_contract_id": 100,
        "candidate_parent_id": 200,
        "relationship_type": "amendment",
        "extracted_parent_reference": "MSA-001",
        "confidence_score": 0.72,
        "model_version": "hierarchy_linker_v1",
        "top_features": json.dumps([
            {"feature": "shared_parties_ratio", "contribution": 5.4},
            {"feature": "title_tfidf_cosine", "contribution": 3.1},
        ]),
        "status": "pending",
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": None,
        "created_at": datetime(2026, 5, 1, 12, 0, 0),
    }
    s.queue[2] = {
        "id": 2,
        "tenant_id": "default",
        "child_contract_id": 100,
        "candidate_parent_id": 300,
        "relationship_type": "amendment",
        "extracted_parent_reference": None,
        "confidence_score": 0.65,
        "model_version": "hierarchy_linker_v1",
        "top_features": None,
        "status": "pending",
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": None,
        "created_at": datetime(2026, 5, 2, 12, 0, 0),
    }

    monkeypatch.setattr(rq_module, "get_connection", lambda: FakeConn(s))
    return s


@pytest.fixture
def client(store):
    # Build a minimal FastAPI app with just the router so we don't need to
    # import the heavy main module (which loads agent framework, OpenAI client,
    # etc.). Auth dependency is overridden to a no-op.
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(rq_module.router)
    app.dependency_overrides[rq_module.get_current_user] = lambda: {
        "preferred_username": "tester@example.com"
    }
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestReviewQueueStats:
    def test_returns_counts_by_status(self, client, store):
        store.queue[3] = {**store.queue[1], "id": 3, "status": "confirmed"}
        store.queue[4] = {**store.queue[1], "id": 4, "status": "rejected"}

        resp = client.get("/api/review-queue/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pending"] == 2
        assert data["confirmed"] == 1
        assert data["rejected"] == 1
        assert data["relinked"] == 0
        assert data["total"] == 4


class TestReviewQueueList:
    def test_list_pending_returns_items_with_child_and_candidate(self, client):
        resp = client.get("/api/review-queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        item = data["items"][0]
        assert item["status"] == "pending"
        assert item["child"]["id"] == 100
        assert item["child"]["title"] == "Amendment to MSA"
        assert item["candidate_parent"]["id"] in {200, 300}
        assert item["model_version"] == "hierarchy_linker_v1"

    def test_list_parses_top_features(self, client):
        resp = client.get("/api/review-queue?limit=1")
        assert resp.status_code == 200
        items = resp.json()["items"]
        # Find the item with top_features (id=1)
        item_with_features = next(
            (i for i in items if i["id"] == 1), items[0]
        )
        if item_with_features["id"] == 1:
            assert len(item_with_features["top_features"]) == 2
            assert item_with_features["top_features"][0]["feature"] == "shared_parties_ratio"

    def test_list_invalid_status_returns_400(self, client):
        resp = client.get("/api/review-queue?status=bogus")
        assert resp.status_code == 400

    def test_paging(self, client):
        resp = client.get("/api/review-queue?limit=1&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["limit"] == 1
        assert data["offset"] == 0
        assert len(data["items"]) == 1


class TestReviewQueueDetail:
    def test_returns_full_detail(self, client):
        resp = client.get("/api/review-queue/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["confidence_score"] == pytest.approx(0.72)
        assert data["child"]["id"] == 100
        assert data["candidate_parent"]["id"] == 200
        assert len(data["top_features"]) == 2

    def test_missing_returns_404(self, client):
        resp = client.get("/api/review-queue/999")
        assert resp.status_code == 404


class TestReviewQueueDecide:
    def test_confirm_creates_relationship_and_marks_confirmed(self, client, store):
        resp = client.post(
            "/api/review-queue/1/decide",
            json={"action": "confirm", "notes": "looks right"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "confirmed"
        assert data["relationship_id"] is not None

        # Queue updated
        assert store.queue[1]["status"] == "confirmed"
        assert store.queue[1]["reviewed_by"] == "tester@example.com"
        assert store.queue[1]["review_notes"] == "looks right"

        # Relationship row created
        rel_id = data["relationship_id"]
        rel = store.relationships[rel_id]
        assert rel["child_contract_id"] == 100
        assert rel["parent_contract_id"] == 200
        assert rel["link_method"] == "ml_review_confirmed"
        assert rel["reviewed_by"] == "tester@example.com"

    def test_reject_does_not_create_relationship(self, client, store):
        resp = client.post(
            "/api/review-queue/1/decide",
            json={"action": "reject", "notes": "wrong parent"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"
        assert resp.json()["relationship_id"] is None
        assert store.queue[1]["status"] == "rejected"
        assert len(store.relationships) == 0

    def test_relink_to_different_parent_creates_manual_relationship(self, client, store):
        resp = client.post(
            "/api/review-queue/1/decide",
            json={"action": "relink", "new_parent_contract_id": 300},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "relinked"
        rel = store.relationships[data["relationship_id"]]
        assert rel["parent_contract_id"] == 300
        assert rel["link_method"] == "manual"

    def test_relink_without_new_parent_returns_400(self, client):
        resp = client.post(
            "/api/review-queue/1/decide",
            json={"action": "relink"},
        )
        assert resp.status_code == 400

    def test_decide_already_decided_returns_409(self, client, store):
        store.queue[1]["status"] = "confirmed"
        resp = client.post(
            "/api/review-queue/1/decide",
            json={"action": "reject"},
        )
        assert resp.status_code == 409

    def test_decide_missing_returns_404(self, client):
        resp = client.post(
            "/api/review-queue/9999/decide",
            json={"action": "reject"},
        )
        assert resp.status_code == 404

    def test_invalid_action_returns_422(self, client):
        resp = client.post(
            "/api/review-queue/1/decide",
            json={"action": "explode"},
        )
        assert resp.status_code == 422
