"""
Inference / Prediction Module

`HierarchyLinker` loads a trained XGBoost model and, given a child
contract plus a set of candidate parents, returns a routing decision:

    auto_link    -> confidence >= AUTO_THRESHOLD
    human_review -> REVIEW_THRESHOLD <= confidence < AUTO_THRESHOLD
    no_link      -> confidence < REVIEW_THRESHOLD

The output also includes the top-K candidates and per-feature
contributions for the chosen parent (lightweight explanations).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np
import xgboost as xgb

from feature_extractor import FEATURE_NAMES, extract_features, features_to_array
from train_model import load_model


AUTO_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.60


@dataclass
class CandidateScore:
    parent_id: int
    confidence: float
    features: dict[str, float]


@dataclass
class LinkPrediction:
    decision: str  # "auto_link" | "human_review" | "no_link"
    parent_id: Optional[int]
    confidence: float
    top_candidates: list[CandidateScore] = field(default_factory=list)
    top_features: list[tuple[str, float]] = field(default_factory=list)


class HierarchyLinker:
    """Loads the trained model and scores child/parent candidate pairs."""

    def __init__(
        self,
        booster: xgb.Booster,
        meta: dict,
        auto_threshold: float = AUTO_THRESHOLD,
        review_threshold: float = REVIEW_THRESHOLD,
    ) -> None:
        self.booster = booster
        self.meta = meta
        self.auto_threshold = auto_threshold
        self.review_threshold = review_threshold

        # Pre-compute global importance ranking for explanations
        importances = meta.get("feature_importance", [])
        self._global_importance = {
            row["feature"]: float(row["gain"]) for row in importances
        }

    @classmethod
    def from_disk(cls, **kwargs) -> "HierarchyLinker":
        booster, meta = load_model()
        return cls(booster, meta, **kwargs)

    def score_pair(
        self,
        child: dict,
        parent: dict,
        idf_cache: dict[str, float],
    ) -> CandidateScore:
        feats = extract_features(child, parent, idf_cache)
        x = features_to_array(feats).reshape(1, -1)
        dmat = xgb.DMatrix(x, feature_names=FEATURE_NAMES)
        score = float(self.booster.predict(dmat)[0])
        return CandidateScore(
            parent_id=int(parent.get("id")),
            confidence=score,
            features=feats,
        )

    def predict_parent(
        self,
        child: dict,
        candidates: Iterable[dict],
        idf_cache: dict[str, float],
        top_k: int = 5,
    ) -> LinkPrediction:
        scored: list[CandidateScore] = [
            self.score_pair(child, p, idf_cache) for p in candidates
        ]
        if not scored:
            return LinkPrediction(decision="no_link", parent_id=None, confidence=0.0)

        scored.sort(key=lambda s: s.confidence, reverse=True)
        best = scored[0]

        if best.confidence >= self.auto_threshold:
            decision = "auto_link"
            parent_id: Optional[int] = best.parent_id
        elif best.confidence >= self.review_threshold:
            decision = "human_review"
            parent_id = best.parent_id
        else:
            decision = "no_link"
            parent_id = None

        # Lightweight explanation: features active for best candidate, weighted by global gain
        active = [
            (name, val * self._global_importance.get(name, 0.0))
            for name, val in best.features.items()
            if val and not np.isnan(val)
        ]
        active.sort(key=lambda kv: kv[1], reverse=True)

        return LinkPrediction(
            decision=decision,
            parent_id=parent_id,
            confidence=best.confidence,
            top_candidates=scored[:top_k],
            top_features=active[:5],
        )


if __name__ == "__main__":
    from feature_extractor import build_idf_cache
    from synthetic_data import generate_corpus

    print("Loading model...")
    linker = HierarchyLinker.from_disk()

    print("Generating corpus...")
    corpus = generate_corpus(num_msas=60, seed=123)  # different seed to test generalization
    idf_cache = build_idf_cache([c.full_text for c in corpus] + [c.title for c in corpus])

    by_id = {c.id: c for c in corpus}
    children = [c for c in corpus if c.true_parent_id is not None]

    # Pick a few example children and show predictions
    sample = children[:5]
    print(f"\nPredicting for {len(sample)} sample children:\n")
    for child in sample:
        # Candidates: all MSAs (a realistic but loose filter)
        cands = [c.to_dict() for c in corpus if c.contract_type == "MSA" and c.id != child.id]
        pred = linker.predict_parent(child.to_dict(), cands, idf_cache, top_k=3)

        true_id = child.true_parent_id
        correct = "OK" if pred.parent_id == true_id else "WRONG"
        print(f"Child {child.id} ({child.contract_type})  true_parent={true_id}")
        print(f"  decision: {pred.decision}  confidence: {pred.confidence:.3f}  "
              f"predicted_parent: {pred.parent_id}  [{correct}]")
        print(f"  top candidates:")
        for s in pred.top_candidates:
            mark = " <- TRUE" if s.parent_id == true_id else ""
            print(f"    parent_id={s.parent_id}  confidence={s.confidence:.3f}{mark}")
        print(f"  top contributing features (active * global_gain):")
        for fname, contrib in pred.top_features:
            print(f"    {fname:30s}  {contrib:.2f}")
        print()
