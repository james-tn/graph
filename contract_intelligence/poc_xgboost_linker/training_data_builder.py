"""
Training Data Builder

For each child contract in a corpus, generate:
  - 1 positive example: (child, true_parent, label=1)
  - K hard negatives: (child, plausible_but_wrong_parent, label=0)
  - K easy negatives: (child, random_unrelated_parent, label=0)

Hard negatives are crucial - they teach the model to distinguish
"correct parent" from "looks-correct-at-first-glance parent" (e.g.,
another MSA for the same client). Easy negatives provide volume.

Returns numpy arrays compatible with sklearn / xgboost.
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np

from feature_extractor import (
    FEATURE_NAMES,
    VALID_HIERARCHY,
    build_idf_cache,
    extract_features,
    features_to_array,
)
from synthetic_data import SyntheticContract


def _client_of(contract: SyntheticContract) -> Optional[str]:
    for p in contract.parties:
        if p.get("role", "").lower() == "client":
            return p["canonical_name"]
    return contract.parties[0]["canonical_name"] if contract.parties else None


def _candidate_parents(
    child: SyntheticContract,
    corpus: list[SyntheticContract],
    by_client: dict[str, list[SyntheticContract]],
) -> list[SyntheticContract]:
    """
    Generate plausible parent candidates for a child:
    - Same client
    - Type compatible (per VALID_HIERARCHY)
    - Effective date precedes child
    """
    valid_parent_types = {
        ptype for ptype, ctypes in VALID_HIERARCHY.items() if child.contract_type in ctypes
    }
    if not valid_parent_types:
        return []

    client = _client_of(child)
    pool = by_client.get(client, []) if client else corpus

    candidates: list[SyntheticContract] = []
    for c in pool:
        if c.id == child.id:
            continue
        if c.contract_type not in valid_parent_types:
            continue
        if c.effective_date > child.effective_date:
            continue
        candidates.append(c)
    return candidates


def build_training_data(
    corpus: list[SyntheticContract],
    hard_negatives_per_positive: int = 3,
    easy_negatives_per_positive: int = 2,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    """
    Build pairwise training data.

    Returns:
        X: (n_pairs, n_features) feature matrix
        y: (n_pairs,) binary labels
        groups: (n_pairs,) child_id per pair (for GroupKFold to prevent leakage)
        meta: list of dicts with debugging info per pair
    """
    rng = random.Random(seed)

    # Build IDF cache from all contract texts
    all_texts = [c.full_text for c in corpus]
    all_titles = [c.title for c in corpus]
    idf_cache = build_idf_cache(all_texts + all_titles)

    # Index corpus
    by_id = {c.id: c for c in corpus}
    by_client: dict[str, list[SyntheticContract]] = {}
    for c in corpus:
        client = _client_of(c)
        if client:
            by_client.setdefault(client, []).append(c)

    children = [c for c in corpus if c.true_parent_id is not None]

    X_rows: list[np.ndarray] = []
    y: list[int] = []
    groups: list[int] = []
    meta: list[dict] = []

    for child in children:
        true_parent = by_id.get(child.true_parent_id)
        if true_parent is None:
            continue

        child_d = child.to_dict()
        true_parent_d = true_parent.to_dict()

        # ---- Positive example ----
        feat_pos = extract_features(child_d, true_parent_d, idf_cache)
        X_rows.append(features_to_array(feat_pos))
        y.append(1)
        groups.append(child.id)
        meta.append({
            "child_id": child.id,
            "parent_id": true_parent.id,
            "label": 1,
            "kind": "positive",
        })

        # ---- Hard negatives: same-client candidates that aren't the true parent ----
        candidates = _candidate_parents(child, corpus, by_client)
        hard_pool = [c for c in candidates if c.id != true_parent.id]
        rng.shuffle(hard_pool)
        for cand in hard_pool[:hard_negatives_per_positive]:
            feat_neg = extract_features(child_d, cand.to_dict(), idf_cache)
            X_rows.append(features_to_array(feat_neg))
            y.append(0)
            groups.append(child.id)
            meta.append({
                "child_id": child.id,
                "parent_id": cand.id,
                "label": 0,
                "kind": "hard_negative",
            })

        # ---- Easy negatives: random parents from the global pool ----
        # Pick MSAs/SOWs from completely different clients
        easy_pool = [
            c for c in corpus
            if c.id != child.id
            and c.id != true_parent.id
            and c.contract_type in ("MSA", "SOW", "Contract")
            and _client_of(c) != _client_of(child)
            and c.effective_date <= child.effective_date
        ]
        rng.shuffle(easy_pool)
        for cand in easy_pool[:easy_negatives_per_positive]:
            feat_neg = extract_features(child_d, cand.to_dict(), idf_cache)
            X_rows.append(features_to_array(feat_neg))
            y.append(0)
            groups.append(child.id)
            meta.append({
                "child_id": child.id,
                "parent_id": cand.id,
                "label": 0,
                "kind": "easy_negative",
            })

    X = np.vstack(X_rows) if X_rows else np.zeros((0, len(FEATURE_NAMES)))
    return X, np.array(y, dtype=np.int64), np.array(groups, dtype=np.int64), meta


def summarize_training_data(y: np.ndarray, meta: list[dict]) -> dict:
    """Quick stats about the generated dataset."""
    kind_counts: dict[str, int] = {}
    for m in meta:
        kind_counts[m["kind"]] = kind_counts.get(m["kind"], 0) + 1

    return {
        "total_pairs": len(y),
        "positives": int(y.sum()),
        "negatives": int((y == 0).sum()),
        "by_kind": kind_counts,
        "positive_rate": float(y.mean()) if len(y) else 0.0,
    }


if __name__ == "__main__":
    from synthetic_data import generate_corpus, corpus_stats

    print("Generating corpus...")
    corpus = generate_corpus(num_msas=60, seed=42)
    print(f"  {corpus_stats(corpus)['total_contracts']} contracts")

    print("\nBuilding training data...")
    X, y, groups, meta = build_training_data(corpus, seed=42)

    stats = summarize_training_data(y, meta)
    print(f"\nTraining set:")
    print(f"  shape: X={X.shape}, y={y.shape}")
    print(f"  positives: {stats['positives']}")
    print(f"  negatives: {stats['negatives']}")
    print(f"  by_kind: {stats['by_kind']}")
    print(f"  positive_rate: {stats['positive_rate']:.3f}")
    print(f"  unique children (groups): {len(np.unique(groups))}")
    print(f"  feature count: {len(FEATURE_NAMES)}")

    # Sanity check: positive examples should have higher mean of strong features
    pos_mask = y == 1
    print(f"\nSanity check (positive vs negative feature means):")
    for fname in ["explicit_ref_exact", "shared_parties_ratio", "type_compatible",
                  "parent_precedes_child", "title_tfidf_cosine"]:
        idx = FEATURE_NAMES.index(fname)
        pos_mean = X[pos_mask, idx].mean()
        neg_mean = X[~pos_mask, idx].mean()
        print(f"  {fname:30s}: pos={pos_mean:.3f}  neg={neg_mean:.3f}")
