"""
Unit tests for the hierarchy_linker module.

These tests exercise the parts that don't need a live database:
  - Feature extractor (deterministic feature vectors)
  - HierarchyLinker scoring against in-memory candidates
  - link_contract orchestrator with a fake DB cursor
  - Threshold logic (auto / review / no-link)

Run with:
    pytest backend/tests/test_hierarchy_linker.py -v
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

# Allow importing data_ingestion modules
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "data_ingestion"))

from hierarchy_linker.feature_extractor import (
    FEATURE_NAMES,
    build_idf_cache,
    extract_features,
    features_to_array,
)
from hierarchy_linker.linker import (
    AUTO_THRESHOLD,
    REVIEW_THRESHOLD,
    HierarchyLinker,
    LinkDecision,
    LinkResult,
    link_contract,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def make_msa(
    contract_id: int = 1,
    reference_number: str = "MSA-ACM-202401-001",
    client: str = "Acme Corp",
    vendor: str = "Vendor Inc",
) -> dict:
    return {
        "id": contract_id,
        "reference_number": reference_number,
        "title": f"Master Services Agreement between {client} and {vendor}",
        "contract_type": "MSA",
        "effective_date": date(2024, 1, 15),
        "expiration_date": date(2026, 1, 15),
        "governing_law": "Delaware",
        "currency": "USD",
        "total_value": 1_000_000.0,
        "full_text": f"This Master Services Agreement is entered into between {client} and {vendor}...",
        "status": "active",
        "parties": [
            {"canonical_name": client, "role": "Client"},
            {"canonical_name": vendor, "role": "Vendor"},
        ],
    }


def make_sow(
    contract_id: int = 2,
    parent_msa: dict | None = None,
    extracted_parent_reference: str | None = None,
    client: str = "Acme Corp",
    vendor: str = "Vendor Inc",
) -> dict:
    parent_ref = parent_msa["reference_number"] if parent_msa else None
    return {
        "id": contract_id,
        "reference_number": f"SOW-ACM-202403-{contract_id:03d}",
        "title": f"SOW - {client}/{vendor}",
        "contract_type": "SOW",
        "effective_date": date(2024, 3, 1),
        "expiration_date": date(2024, 9, 1),
        "governing_law": "Delaware",
        "currency": "USD",
        "total_value": 50_000.0,
        "full_text": (
            f"This Statement of Work is issued under the terms of the master agreement "
            f"{parent_ref or '[unknown]'} dated 2024-01-15. The parties are {client} and {vendor}."
        ),
        "status": "active",
        "parties": [
            {"canonical_name": client, "role": "Client"},
            {"canonical_name": vendor, "role": "Vendor"},
        ],
        "extracted_parent_reference": extracted_parent_reference,
    }


@pytest.fixture
def idf_cache() -> dict[str, float]:
    return build_idf_cache([
        "Master Services Agreement between Acme Corp and Vendor Inc",
        "Statement of Work issued under master agreement",
        "Some unrelated text about widgets and gadgets",
    ])


# ---------------------------------------------------------------------------
# Feature extractor tests
# ---------------------------------------------------------------------------

class TestFeatureExtractor:

    def test_features_have_stable_order(self, idf_cache):
        msa = make_msa()
        sow = make_sow(parent_msa=msa)
        feats = extract_features(sow, msa, idf_cache)
        assert list(feats.keys()) == FEATURE_NAMES

    def test_feature_array_length_matches_names(self, idf_cache):
        msa = make_msa()
        sow = make_sow(parent_msa=msa)
        arr = features_to_array(extract_features(sow, msa, idf_cache))
        assert arr.shape == (len(FEATURE_NAMES),)

    def test_true_parent_features_are_strong(self, idf_cache):
        msa = make_msa()
        sow = make_sow(parent_msa=msa, extracted_parent_reference=msa["reference_number"])
        feats = extract_features(sow, msa, idf_cache)
        assert feats["explicit_ref_exact"] == 1.0
        assert feats["explicit_ref_fuzzy"] == 1.0
        assert feats["shared_parties_ratio"] == 1.0
        assert feats["client_match"] == 1.0
        assert feats["vendor_match"] == 1.0
        assert feats["type_compatible"] == 1.0
        assert feats["governing_law_match"] == 1.0
        assert feats["parent_precedes_child"] == 1.0
        assert feats["child_within_parent_term"] == 1.0
        assert feats["parent_is_msa"] == 1.0
        assert feats["child_is_sow"] == 1.0

    def test_unrelated_parent_features_are_weak(self, idf_cache):
        msa = make_msa(contract_id=1, client="Acme Corp", vendor="Vendor Inc")
        # Unrelated MSA: different parties, different governing law
        unrelated = make_msa(
            contract_id=99, reference_number="MSA-XYZ-202101-001",
            client="Other Corp", vendor="Different Vendor",
        )
        unrelated["governing_law"] = "California"
        sow = make_sow(parent_msa=msa)
        feats = extract_features(sow, unrelated, idf_cache)
        assert feats["shared_parties_ratio"] == 0.0
        assert feats["client_match"] == 0.0
        assert feats["explicit_ref_exact"] == 0.0
        assert feats["governing_law_match"] == 0.0

    def test_corrupted_reference_still_scores_high_on_fuzzy(self, idf_cache):
        msa = make_msa(reference_number="MSA-ACM-202401-001")
        sow = make_sow(
            parent_msa=msa,
            extracted_parent_reference="msa/acm/202401/001",  # mangled separators+case
        )
        feats = extract_features(sow, msa, idf_cache)
        # Exact text-substring match should fail (slashes won't match raw "MSA-..."
        # in the text body), but the normalized fuzzy score should still be ~1.0
        assert feats["explicit_ref_fuzzy"] >= 0.95

    def test_missing_dates_become_nan(self, idf_cache):
        msa = make_msa()
        sow = make_sow(parent_msa=msa)
        sow["effective_date"] = None
        feats = extract_features(sow, msa, idf_cache)

        import math
        assert math.isnan(feats["days_between_effective"])
        assert math.isnan(feats["log_days_gap"])

    def test_invalid_hierarchy_marks_type_incompatible(self, idf_cache):
        # SOW cannot parent another SOW
        sow1 = make_sow(contract_id=1)
        sow1["contract_type"] = "SOW"
        sow2 = make_sow(contract_id=2)
        sow2["contract_type"] = "SOW"
        feats = extract_features(sow2, sow1, idf_cache)
        # SOW -> SOW is NOT in VALID_HIERARCHY for SOW children
        # Actually SOW.children = {Amendment, WorkOrder, Addendum}, so SOW->SOW is invalid
        assert feats["type_compatible"] == 0.0


# ---------------------------------------------------------------------------
# HierarchyLinker tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def loaded_linker():
    """Load the model trained by run_poc.py. Skips if not yet present."""
    model_path = (
        PROJECT_ROOT / "data_ingestion" / "hierarchy_linker" / "models"
        / "hierarchy_linker_v1.json"
    )
    if not model_path.exists():
        pytest.skip(f"Model not found at {model_path}; run scripts/train_hierarchy_linker.py")
    return HierarchyLinker.from_disk()


class TestHierarchyLinkerInference:

    def test_perfect_candidate_scores_high(self, loaded_linker, idf_cache):
        msa = make_msa()
        sow = make_sow(parent_msa=msa, extracted_parent_reference=msa["reference_number"])
        score = loaded_linker.score_pair(sow, msa, idf_cache)
        assert score.confidence > 0.9

    def test_unrelated_candidate_scores_low(self, loaded_linker, idf_cache):
        msa = make_msa(contract_id=1)
        unrelated = make_msa(
            contract_id=99,
            reference_number="MSA-XYZ-202101-001",
            client="Other Corp",
            vendor="Different Vendor",
        )
        sow = make_sow(parent_msa=msa)
        score = loaded_linker.score_pair(sow, unrelated, idf_cache)
        assert score.confidence < 0.5

    def test_predict_parent_picks_correct_candidate(self, loaded_linker):
        true_parent = make_msa(contract_id=1)
        decoy = make_msa(
            contract_id=2,
            reference_number="MSA-XYZ-202101-001",
            client="Other Corp",
            vendor="Different Vendor",
        )
        sow = make_sow(parent_msa=true_parent)
        result = loaded_linker.predict_parent(sow, [true_parent, decoy])
        # The ranking should always put the true parent first, even if the
        # absolute confidence varies based on how rich the IDF corpus is.
        assert len(result.top_candidates) == 2
        assert result.top_candidates[0].parent_id == true_parent["id"]
        assert result.top_candidates[0].confidence > result.top_candidates[1].confidence

    def test_empty_candidates_returns_no_link(self, loaded_linker):
        sow = make_sow(parent_msa=make_msa())
        result = loaded_linker.predict_parent(sow, [])
        assert result.decision == LinkDecision.NO_LINK
        assert result.parent_id is None
        assert result.confidence == 0.0


# ---------------------------------------------------------------------------
# Orchestrator tests with a fake DB cursor
# ---------------------------------------------------------------------------

class FakeCursor:
    """Minimal fake cursor that responds to the rule-based lookup query.
    Used to test link_contract without a real database."""

    def __init__(self, ref_to_id: dict[str, int] | None = None):
        self._ref_to_id = ref_to_id or {}
        self._last_result = None

    def execute(self, sql: str, params=None):
        sql_lower = sql.lower()
        # Only the rule-based exact-match query needs to work in these tests
        if "select id from contracts" in sql_lower and "reference_number" in sql_lower:
            ref = params[2] if params and len(params) >= 3 else None
            cid = self._ref_to_id.get(ref) if ref else None
            self._last_result = {"id": cid} if cid is not None else None
        else:
            self._last_result = None

    def fetchone(self):
        return self._last_result

    def fetchall(self):
        return []


class TestLinkContractOrchestrator:

    def test_rule_based_match_short_circuits(self):
        cur = FakeCursor(ref_to_id={"MSA-ACM-202401-001": 42})
        result = link_contract(
            cur,
            child_contract_id=2,
            extracted_parent_reference="MSA-ACM-202401-001",
            linker=None,                # ML disabled
            enable_ml_fallback=False,
        )
        assert result.decision == LinkDecision.RULE_LINK
        assert result.parent_id == 42
        assert result.confidence == 1.0
        assert result.method == "rule_based"

    def test_rule_miss_with_no_linker_returns_no_link(self):
        cur = FakeCursor(ref_to_id={})
        result = link_contract(
            cur,
            child_contract_id=2,
            extracted_parent_reference="MSA-DOES-NOT-EXIST",
            linker=None,
            enable_ml_fallback=False,
        )
        assert result.decision == LinkDecision.NO_LINK
        assert result.parent_id is None
        assert result.method == "none"

    def test_no_extracted_reference_with_no_linker_returns_no_link(self):
        cur = FakeCursor(ref_to_id={})
        result = link_contract(
            cur,
            child_contract_id=2,
            extracted_parent_reference=None,
            linker=None,
            enable_ml_fallback=False,
        )
        assert result.decision == LinkDecision.NO_LINK


class TestLinkResult:

    def test_link_result_serializes_top_features(self):
        from hierarchy_linker.linker import _serialize_top_features

        result = LinkResult(
            decision=LinkDecision.AUTO_LINK,
            parent_id=1,
            confidence=0.95,
            method="ml_auto",
            top_features=[
                ("shared_parties_ratio", 142.7),
                ("title_tfidf_cosine", 91.2),
            ],
        )
        serialized = _serialize_top_features(result)
        assert serialized is not None
        assert "shared_parties_ratio" in serialized
        assert "142.7" in serialized

    def test_thresholds_have_sane_defaults(self):
        assert AUTO_THRESHOLD > REVIEW_THRESHOLD
        assert AUTO_THRESHOLD <= 1.0
        assert REVIEW_THRESHOLD >= 0.0
