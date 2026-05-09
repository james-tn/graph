"""
Production hierarchy linker.

Wraps a trained XGBoost model (from poc_xgboost_linker/ or trained against
real data via scripts/train_hierarchy_linker.py) and exposes the inference
+ orchestration entry points called by the ingestion pipeline.

Public surface:
    HierarchyLinker  - loadable model wrapper, scores (child, parent) pairs.
    LinkDecision     - enum: AUTO_LINK | HUMAN_REVIEW | NO_LINK | RULE_LINK
    LinkResult       - dataclass returned by link_contract().
    link_contract()  - the orchestrator the ingestion pipeline calls.

Cascade (the orchestrator):
    1. Rule-based exact match on extracted_parent_reference == reference_number
       -> if hit, return RULE_LINK with confidence 1.0.
    2. Otherwise, fetch DB-backed candidates, score with XGBoost.
       - top1 conf >= AUTO_THRESHOLD  -> AUTO_LINK
       - top1 conf >= REVIEW_THRESHOLD -> HUMAN_REVIEW (queue, do not link)
       - else                         -> NO_LINK
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional

import numpy as np

from .candidate_generator import fetch_candidate_parents, fetch_child_contract_dict
from .calibration import Calibrator
from .feature_extractor import (
    FEATURE_NAMES,
    build_idf_cache,
    extract_features,
    features_to_array,
)


# Default thresholds. Override in calls if you want to be more conservative
# during phase 2 rollout.
AUTO_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.60

DEFAULT_MODEL_PATH = os.environ.get(
    "HIERARCHY_LINKER_MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "models", "hierarchy_linker_v1.json"),
)
DEFAULT_META_PATH = os.environ.get(
    "HIERARCHY_LINKER_META_PATH",
    os.path.join(os.path.dirname(__file__), "models", "hierarchy_linker_v1.meta.json"),
)


class LinkDecision(str, Enum):
    RULE_LINK = "rule_link"          # exact reference_number match — 100% precision
    AUTO_LINK = "ml_auto"            # ML confidence >= AUTO_THRESHOLD
    HUMAN_REVIEW = "ml_review"       # REVIEW_THRESHOLD <= ML confidence < AUTO_THRESHOLD
    NO_LINK = "no_link"              # below review threshold


@dataclass
class CandidateScore:
    parent_id: int
    confidence: float
    features: dict[str, float]
    raw_score: Optional[float] = None  # uncalibrated booster output, if calibration applied


@dataclass
class LinkResult:
    decision: LinkDecision
    parent_id: Optional[int]
    confidence: float
    method: str                      # 'rule_based' | 'ml_auto' | 'ml_review' | 'none'
    model_version: Optional[str] = None
    top_candidates: list[CandidateScore] = field(default_factory=list)
    top_features: list[tuple[str, float]] = field(default_factory=list)
    calibration_method: str = "none"


class HierarchyLinker:
    """Loadable wrapper around the trained XGBoost booster."""

    def __init__(
        self,
        booster,
        meta: dict,
        auto_threshold: float = AUTO_THRESHOLD,
        review_threshold: float = REVIEW_THRESHOLD,
    ) -> None:
        self.booster = booster
        self.meta = meta
        self.auto_threshold = auto_threshold
        self.review_threshold = review_threshold

        importances = meta.get("feature_importance", []) or []
        self._global_importance = {
            row["feature"]: float(row.get("gain", 0.0)) for row in importances
        }
        self.model_version = meta.get("model_version") or meta.get("version") or "v1"
        self.calibrator = Calibrator.from_meta(meta)

    # ----- loaders -----------------------------------------------------------

    @classmethod
    def from_disk(
        cls,
        model_path: str = DEFAULT_MODEL_PATH,
        meta_path: str = DEFAULT_META_PATH,
        **kwargs,
    ) -> "HierarchyLinker":
        # Lazy import so importing this module doesn't pull in xgboost
        # (the rule-based ingestion path can run without ML deps installed).
        import xgboost as xgb

        booster = xgb.Booster()
        booster.load_model(model_path)

        meta: dict = {}
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
        return cls(booster, meta, **kwargs)

    # ----- scoring -----------------------------------------------------------

    def score_pair(
        self,
        child: dict,
        parent: dict,
        idf_cache: dict[str, float],
    ) -> CandidateScore:
        import xgboost as xgb

        feats = extract_features(child, parent, idf_cache)
        x = features_to_array(feats).reshape(1, -1)
        dmat = xgb.DMatrix(x, feature_names=FEATURE_NAMES)
        raw = float(self.booster.predict(dmat)[0])
        if self.calibrator.method == "none":
            calibrated = raw
            raw_for_log: Optional[float] = None
        else:
            calibrated = self.calibrator.transform_one(raw)
            raw_for_log = raw
        return CandidateScore(
            parent_id=int(parent.get("id")),
            confidence=calibrated,
            features=feats,
            raw_score=raw_for_log,
        )

    def predict_parent(
        self,
        child: dict,
        candidates: Iterable[dict],
        idf_cache: Optional[dict[str, float]] = None,
        top_k: int = 5,
    ) -> LinkResult:
        candidates = list(candidates)
        if idf_cache is None:
            idf_cache = build_idf_cache(
                [child.get("full_text", "") or ""]
                + [c.get("full_text", "") or "" for c in candidates]
                + [child.get("title", "") or ""]
                + [c.get("title", "") or "" for c in candidates]
            )

        if not candidates:
            return LinkResult(
                decision=LinkDecision.NO_LINK,
                parent_id=None,
                confidence=0.0,
                method="none",
                model_version=self.model_version,
                calibration_method=self.calibrator.method,
            )

        scored = [self.score_pair(child, p, idf_cache) for p in candidates]
        scored.sort(key=lambda s: s.confidence, reverse=True)
        best = scored[0]

        if best.confidence >= self.auto_threshold:
            decision = LinkDecision.AUTO_LINK
            parent_id: Optional[int] = best.parent_id
            method = "ml_auto"
        elif best.confidence >= self.review_threshold:
            decision = LinkDecision.HUMAN_REVIEW
            parent_id = best.parent_id
            method = "ml_review"
        else:
            decision = LinkDecision.NO_LINK
            parent_id = None
            method = "none"

        active = [
            (name, val * self._global_importance.get(name, 0.0))
            for name, val in best.features.items()
            if val and not (isinstance(val, float) and np.isnan(val))
        ]
        active.sort(key=lambda kv: kv[1], reverse=True)

        return LinkResult(
            decision=decision,
            parent_id=parent_id,
            confidence=best.confidence,
            method=method,
            model_version=self.model_version,
            top_candidates=scored[:top_k],
            top_features=active[:5],
            calibration_method=self.calibrator.method,
        )


# ---------------------------------------------------------------------------
# Orchestrator: rule-based first, ML fallback
# ---------------------------------------------------------------------------

def _rule_based_lookup(
    cur,
    extracted_parent_reference: Optional[str],
    child_contract_id: int,
    tenant_id: str = "default",
) -> Optional[int]:
    """Mirror the existing rule-based linker: exact reference_number match."""
    if not extracted_parent_reference:
        return None
    ref = extracted_parent_reference.strip()
    if not ref:
        return None
    cur.execute(
        """
        SELECT id FROM contracts
        WHERE tenant_id = %s
          AND id != %s
          AND reference_number = %s
        LIMIT 1
        """,
        (tenant_id, child_contract_id, ref),
    )
    row = cur.fetchone()
    if not row:
        return None
    if isinstance(row, dict):
        return row.get("id")
    return row[0]


def link_contract(
    cur,
    child_contract_id: int,
    extracted_parent_reference: Optional[str],
    linker: Optional[HierarchyLinker] = None,
    tenant_id: str = "default",
    auto_threshold: float = AUTO_THRESHOLD,
    review_threshold: float = REVIEW_THRESHOLD,
    enable_ml_fallback: bool = True,
    max_candidates: int = 50,
) -> LinkResult:
    """
    Run the link cascade for a single child contract.

    1. Rule-based exact match on reference_number  -> RULE_LINK if found.
    2. Otherwise, if `enable_ml_fallback` and a `linker` is provided,
       fetch candidates from the DB and score them with the ML model.

    The caller is responsible for writing the result back into
    `contract_relationships` (via the helpers below or its own SQL).
    """
    # ----- 1. Rule-based -----------------------------------------------------
    rule_hit = _rule_based_lookup(cur, extracted_parent_reference, child_contract_id, tenant_id)
    if rule_hit is not None:
        return LinkResult(
            decision=LinkDecision.RULE_LINK,
            parent_id=rule_hit,
            confidence=1.0,
            method="rule_based",
            model_version=None,
        )

    # ----- 2. ML fallback ----------------------------------------------------
    if not enable_ml_fallback or linker is None:
        return LinkResult(
            decision=LinkDecision.NO_LINK,
            parent_id=None,
            confidence=0.0,
            method="none",
        )

    # Pull child + candidate dicts from the DB
    child = fetch_child_contract_dict(cur, child_contract_id, extracted_parent_reference)

    candidates = fetch_candidate_parents(
        cur,
        child_contract_id=child_contract_id,
        child_contract_type=child.get("contract_type"),
        child_effective_date=child.get("effective_date"),
        tenant_id=tenant_id,
        max_candidates=max_candidates,
    )

    # Apply thresholds via predict_parent
    linker.auto_threshold = auto_threshold
    linker.review_threshold = review_threshold
    return linker.predict_parent(child, candidates)


# ---------------------------------------------------------------------------
# Persistence helpers — write a LinkResult into the database
# ---------------------------------------------------------------------------

def _serialize_top_features(result: LinkResult) -> Optional[str]:
    if not result.top_features:
        return None
    return json.dumps([
        {"feature": name, "contribution": round(float(c), 4)}
        for name, c in result.top_features
    ])


def write_link_result(
    cur,
    child_contract_id: int,
    extracted_parent_reference: Optional[str],
    relationship_type: str,
    result: LinkResult,
    relationship_description: Optional[str] = None,
    tenant_id: str = "default",
) -> None:
    """
    Persist the cascade outcome:
      - RULE_LINK / AUTO_LINK: insert into contract_relationships with method/confidence
      - HUMAN_REVIEW: insert pending row into link_review_queue (do NOT create a link yet)
      - NO_LINK: insert contract_relationships row with NULL parent_contract_id but
                 keep parent_reference_number (matches existing fallback behavior)
    """
    top_features_json = _serialize_top_features(result)

    if result.decision in (LinkDecision.RULE_LINK, LinkDecision.AUTO_LINK):
        cur.execute(
            """
            INSERT INTO contract_relationships (
                tenant_id,
                child_contract_id,
                parent_contract_id,
                parent_reference_number,
                relationship_type,
                relationship_description,
                link_method,
                confidence_score,
                model_version,
                top_features
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (child_contract_id, parent_contract_id, relationship_type) DO NOTHING
            """,
            (
                tenant_id,
                child_contract_id,
                result.parent_id,
                extracted_parent_reference,
                relationship_type,
                relationship_description,
                result.method,
                result.confidence if result.confidence > 0 else None,
                result.model_version,
                top_features_json,
            ),
        )
        return

    if result.decision == LinkDecision.HUMAN_REVIEW:
        cur.execute(
            """
            INSERT INTO link_review_queue (
                tenant_id,
                child_contract_id,
                candidate_parent_id,
                relationship_type,
                confidence_score,
                model_version,
                top_features,
                extracted_parent_reference
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            """,
            (
                tenant_id,
                child_contract_id,
                result.parent_id,
                relationship_type,
                result.confidence,
                result.model_version,
                top_features_json,
                extracted_parent_reference,
            ),
        )
        return

    # NO_LINK: keep the historical behavior of recording the orphaned reference
    if extracted_parent_reference:
        cur.execute(
            """
            INSERT INTO contract_relationships (
                tenant_id,
                child_contract_id,
                parent_contract_id,
                parent_reference_number,
                relationship_type,
                relationship_description,
                link_method,
                confidence_score,
                model_version
            )
            VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (child_contract_id, parent_contract_id, relationship_type) DO NOTHING
            """,
            (
                tenant_id,
                child_contract_id,
                extracted_parent_reference,
                relationship_type,
                relationship_description,
                "none",
                None,
                result.model_version,
            ),
        )
