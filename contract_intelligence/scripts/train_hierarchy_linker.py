#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Train the hierarchy linker model.

Two training modes:

  1. --bootstrap  (default if the DB has fewer than --min-real-positives
     confirmed parent links)
     Trains on the synthetic POC corpus to seed a working model. Useful
     for cold start; gives ~100% accuracy on synthetic but may need
     fine-tuning on production data.

  2. --from-db    (recommended once enough real labels exist)
     Pulls confirmed (rule_based, ml_review_confirmed, manual) parent
     links from contract_relationships, queries the matching contract
     rows + parties + monetary_values, builds positives + hard/easy
     negatives via the candidate generator, and trains.

The output is two files in
  contract_intelligence/data_ingestion/hierarchy_linker/models/
    hierarchy_linker_v1.json       (XGBoost booster)
    hierarchy_linker_v1.meta.json  (feature names, importance, training info)

Usage:
    python scripts/train_hierarchy_linker.py --bootstrap
    python scripts/train_hierarchy_linker.py --from-db --min-real-positives 200
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import date, datetime
from pathlib import Path

import numpy as np

# Path setup: run from project root or scripts/.
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "data_ingestion"))
sys.path.insert(0, str(PROJECT_ROOT / "poc_xgboost_linker"))

from hierarchy_linker.feature_extractor import (
    FEATURE_NAMES,
    build_idf_cache,
    extract_features,
    features_to_array,
)
from hierarchy_linker.candidate_generator import (
    allowed_parent_types,
    fetch_candidate_parents,
    fetch_child_contract_dict,
)


MODELS_DIR = PROJECT_ROOT / "data_ingestion" / "hierarchy_linker" / "models"
MODEL_PATH = MODELS_DIR / "hierarchy_linker_v1.json"
META_PATH = MODELS_DIR / "hierarchy_linker_v1.meta.json"


# ---------------------------------------------------------------------------
# DB-backed training data extraction
# ---------------------------------------------------------------------------

CONFIRMED_LINK_METHODS = ("rule_based", "ml_review_confirmed", "manual")


def fetch_real_positives(cur, tenant_id: str = "default") -> list[tuple[int, int, str]]:
    """Return [(child_id, parent_id, relationship_type)] of trusted links."""
    cur.execute(
        """
        SELECT child_contract_id, parent_contract_id, relationship_type
        FROM contract_relationships
        WHERE tenant_id = %s
          AND parent_contract_id IS NOT NULL
          AND link_method = ANY(%s)
        """,
        (tenant_id, list(CONFIRMED_LINK_METHODS)),
    )
    return [(r["child_contract_id"], r["parent_contract_id"], r["relationship_type"])
            for r in cur.fetchall()]


def fetch_rejected_pairs(cur, tenant_id: str = "default") -> list[tuple[int, int, str]]:
    """Return [(child_id, candidate_parent_id, relationship_type)] of pairs a
    human reviewer explicitly rejected. These are high-quality labeled
    negatives that we should always include in training.
    """
    cur.execute(
        """
        SELECT child_contract_id, candidate_parent_id, relationship_type
        FROM link_review_queue
        WHERE tenant_id = %s
          AND status = 'rejected'
          AND candidate_parent_id IS NOT NULL
        """,
        (tenant_id,),
    )
    return [
        (r["child_contract_id"], r["candidate_parent_id"], r["relationship_type"] or "related")
        for r in cur.fetchall()
    ]


def build_real_training_data(
    cur,
    tenant_id: str = "default",
    hard_negatives_per_positive: int = 5,
    easy_negatives_per_positive: int = 2,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    """Build training pairs from real DB links.

    Sources:
      - Positives: trusted links from contract_relationships (rule_based,
        ml_review_confirmed, manual)
      - Reviewer-rejected negatives: pairs explicitly rejected in
        link_review_queue (highest-quality negatives)
      - Hard negatives: candidate-generator output minus the true parent
      - Easy negatives: random plausible-type contracts that share NO party
    """
    rng = random.Random(seed)

    positives = fetch_real_positives(cur, tenant_id)
    rejected = fetch_rejected_pairs(cur, tenant_id)
    print(f"  Found {len(positives)} confirmed parent links in DB")
    print(f"  Found {len(rejected)} reviewer-rejected pairs (labeled negatives)")
    if not positives:
        return (
            np.zeros((0, len(FEATURE_NAMES))),
            np.array([], dtype=np.int64),
            np.array([], dtype=np.int64),
            [],
        )

    # Pre-fetch all contract texts for IDF
    cur.execute(
        "SELECT title, COALESCE(source_markdown, '') AS full_text FROM contracts WHERE tenant_id = %s",
        (tenant_id,),
    )
    all_rows = cur.fetchall()
    idf_cache = build_idf_cache(
        [r["full_text"] for r in all_rows] + [r["title"] for r in all_rows]
    )

    X_rows: list[np.ndarray] = []
    y: list[int] = []
    groups: list[int] = []
    meta: list[dict] = []

    for child_id, parent_id, rel_type in positives:
        try:
            child = fetch_child_contract_dict(cur, child_id)
        except ValueError:
            continue
        try:
            parent = fetch_child_contract_dict(cur, parent_id)
        except ValueError:
            continue

        # Positive
        X_rows.append(features_to_array(extract_features(child, parent, idf_cache)))
        y.append(1)
        groups.append(child_id)
        meta.append({"child_id": child_id, "parent_id": parent_id, "kind": "positive"})

        # Hard negatives: candidate generator output minus the true parent
        candidates = fetch_candidate_parents(
            cur,
            child_contract_id=child_id,
            child_contract_type=child.get("contract_type"),
            child_effective_date=child.get("effective_date"),
            tenant_id=tenant_id,
            max_candidates=20,
        )
        hard_pool = [c for c in candidates if c["id"] != parent_id]
        rng.shuffle(hard_pool)
        for cand in hard_pool[:hard_negatives_per_positive]:
            X_rows.append(features_to_array(extract_features(child, cand, idf_cache)))
            y.append(0)
            groups.append(child_id)
            meta.append({"child_id": child_id, "parent_id": cand["id"], "kind": "hard_negative"})

        # Easy negatives: random plausible-type contracts that share NO party
        cur.execute(
            """
            SELECT c.id, c.reference_number, c.title, c.contract_type,
                   c.effective_date, c.expiration_date, c.governing_law, c.status,
                   c.source_markdown AS full_text,
                   '[]'::json AS parties, NULL::numeric AS total_value, NULL::text AS currency
            FROM contracts c
            WHERE c.tenant_id = %s
              AND c.id != %s
              AND c.id != %s
              AND c.contract_type = ANY(%s)
              AND c.id NOT IN (
                  SELECT pc.contract_id
                  FROM parties_contracts pc
                  WHERE pc.party_id IN (
                      SELECT party_id FROM parties_contracts WHERE contract_id = %s
                  )
              )
            ORDER BY random()
            LIMIT %s
            """,
            (
                tenant_id,
                child_id,
                parent_id,
                allowed_parent_types(child.get("contract_type", "")),
                child_id,
                easy_negatives_per_positive,
            ),
        )
        for row in cur.fetchall():
            cand = dict(row)
            cand["parties"] = []
            X_rows.append(features_to_array(extract_features(child, cand, idf_cache)))
            y.append(0)
            groups.append(child_id)
            meta.append({"child_id": child_id, "parent_id": cand["id"], "kind": "easy_negative"})

    # Reviewer-rejected pairs: explicit labeled negatives.
    for child_id, cand_id, _rel_type in rejected:
        try:
            child = fetch_child_contract_dict(cur, child_id)
            cand = fetch_child_contract_dict(cur, cand_id)
        except ValueError:
            continue
        X_rows.append(features_to_array(extract_features(child, cand, idf_cache)))
        y.append(0)
        groups.append(child_id)
        meta.append({"child_id": child_id, "parent_id": cand_id, "kind": "reviewer_rejected"})

    return (
        np.vstack(X_rows) if X_rows else np.zeros((0, len(FEATURE_NAMES))),
        np.array(y, dtype=np.int64),
        np.array(groups, dtype=np.int64),
        meta,
    )


# ---------------------------------------------------------------------------
# Bootstrap from synthetic data (re-uses the POC pipeline)
# ---------------------------------------------------------------------------

def build_synthetic_training_data(num_msas: int = 60, seed: int = 42):
    """Re-uses the synthetic generator + builder from poc_xgboost_linker/."""
    from synthetic_data import generate_corpus
    from training_data_builder import build_training_data

    corpus = generate_corpus(num_msas=num_msas, seed=seed)
    return build_training_data(
        corpus,
        hard_negatives_per_positive=5,
        easy_negatives_per_positive=2,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_and_save(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    source: str,
    num_boost_round: int = 500,
    early_stopping_rounds: int = 30,
    min_boost_round: int = 150,
) -> None:
    import xgboost as xgb
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.model_selection import GroupKFold

    pos = max(int(y.sum()), 1)
    neg = max(int((y == 0).sum()), 1)
    scale_pos_weight = float(np.sqrt(neg / pos))

    params = {
        "objective": "binary:logistic",
        "eval_metric": "aucpr",
        "tree_method": "hist",
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 1.0,
        "reg_lambda": 1.0,
        "scale_pos_weight": scale_pos_weight,
        "seed": 42,
    }

    # Cross-validate via GroupKFold (5 splits)
    print("\n[CV] GroupKFold(5) cross-validation:")
    gkf = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    aucs, auprs = [], []
    best_iters = []
    for fold_i, (tr, va) in enumerate(gkf.split(X, y, groups), start=1):
        dtr = xgb.DMatrix(X[tr], label=y[tr], feature_names=FEATURE_NAMES)
        dva = xgb.DMatrix(X[va], label=y[va], feature_names=FEATURE_NAMES)
        booster = xgb.train(
            params, dtr, num_boost_round=num_boost_round,
            evals=[(dva, "val")],
            early_stopping_rounds=early_stopping_rounds,
            verbose_eval=False,
        )
        bi = booster.best_iteration if booster.best_iteration is not None else (booster.num_boosted_rounds() - 1)
        scores = booster.predict(dva, iteration_range=(0, bi + 1))
        aucs.append(roc_auc_score(y[va], scores))
        auprs.append(average_precision_score(y[va], scores))
        best_iters.append(bi)
        print(f"  Fold {fold_i}: AUC={aucs[-1]:.4f}  AUCPR={auprs[-1]:.4f}  best_iter={bi}")

    cv_mean_auc = float(np.mean(aucs)) if aucs else 0.0
    cv_mean_aucpr = float(np.mean(auprs)) if auprs else 0.0
    print(f"  Mean AUC: {cv_mean_auc:.4f}  Mean AUCPR: {cv_mean_aucpr:.4f}")

    # Final training on full data
    print("\n[Final] Training on full data...")
    gkf2 = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    tr_idx, va_idx = next(gkf2.split(X, y, groups))
    dtr = xgb.DMatrix(X[tr_idx], label=y[tr_idx], feature_names=FEATURE_NAMES)
    dva = xgb.DMatrix(X[va_idx], label=y[va_idx], feature_names=FEATURE_NAMES)
    early_booster = xgb.train(
        params, dtr, num_boost_round=num_boost_round,
        evals=[(dva, "val")],
        early_stopping_rounds=early_stopping_rounds,
        verbose_eval=False,
    )
    best_iter = early_booster.best_iteration if early_booster.best_iteration is not None else (early_booster.num_boosted_rounds() - 1)
    final_rounds = max(int(best_iter) + 1, min_boost_round)

    dfull = xgb.DMatrix(X, label=y, feature_names=FEATURE_NAMES)
    final = xgb.train(params, dfull, num_boost_round=final_rounds, verbose_eval=False)

    # Importance
    score = final.get_score(importance_type="gain")
    importances = sorted(
        [(name, float(score.get(name, 0.0))) for name in FEATURE_NAMES],
        key=lambda kv: kv[1], reverse=True,
    )

    # Save
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    final.save_model(str(MODEL_PATH))
    meta_payload = {
        "model_version": "hierarchy_linker_v1",
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "training_source": source,
        "feature_names": FEATURE_NAMES,
        "training_info": {
            "n_train": int(len(y)),
            "n_positives": int(y.sum()),
            "n_negatives": int((y == 0).sum()),
            "scale_pos_weight": scale_pos_weight,
            "num_boost_round": int(final_rounds),
            "best_iteration": int(best_iter),
            "params": params,
        },
        "cv_metrics": {
            "mean_auc": cv_mean_auc,
            "mean_aucpr": cv_mean_aucpr,
            "n_folds": len(aucs),
        },
        "feature_importance": [{"feature": n, "gain": g} for n, g in importances],
    }
    with open(META_PATH, "w") as f:
        json.dump(meta_payload, f, indent=2, default=str)

    print(f"\n  Saved model -> {MODEL_PATH}")
    print(f"  Saved meta  -> {META_PATH}")
    print("  Top 10 features:")
    for name, gain in importances[:10]:
        print(f"    {name:30s}  gain={gain:.2f}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Train the hierarchy linker model")
    parser.add_argument("--bootstrap", action="store_true",
                        help="Train on synthetic data (good for cold-start)")
    parser.add_argument("--from-db", action="store_true",
                        help="Train from confirmed parent links in PostgreSQL")
    parser.add_argument("--min-real-positives", type=int, default=200,
                        help="With --from-db, fall back to bootstrap if fewer real positives exist")
    parser.add_argument("--tenant-id", default="default")
    args = parser.parse_args()

    if not args.bootstrap and not args.from_db:
        print("Defaulting to --bootstrap (no --from-db specified)")
        args.bootstrap = True

    if args.from_db:
        from postgres_ingestion import get_db_connection

        print("=" * 70)
        print("Training from real DB links")
        print("=" * 70)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            X, y, groups, meta = build_real_training_data(cur, tenant_id=args.tenant_id)
        finally:
            cur.close()
            conn.close()

        n_pos = int(y.sum()) if len(y) else 0
        if n_pos < args.min_real_positives:
            print(f"\n  ⚠ Only {n_pos} real positives (< {args.min_real_positives}); "
                  f"falling back to bootstrap.")
            args.bootstrap = True
        else:
            print(f"  pairs: {len(y)}  positives: {n_pos}  "
                  f"negatives: {int((y == 0).sum())}")
            train_and_save(X, y, groups, source="postgres")
            return

    if args.bootstrap:
        print("=" * 70)
        print("Bootstrap training on synthetic POC corpus")
        print("=" * 70)
        X, y, groups, meta = build_synthetic_training_data()
        n_pos = int(y.sum())
        print(f"  pairs: {len(y)}  positives: {n_pos}  "
              f"negatives: {int((y == 0).sum())}")
        train_and_save(X, y, groups, source="synthetic_bootstrap")


if __name__ == "__main__":
    main()
