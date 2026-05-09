"""
XGBoost Trainer for Contract Hierarchy Linker

Trains a binary classifier that scores (child, candidate_parent) pairs.
Uses GroupKFold by child_id to prevent leakage (the same child must not
appear in both train and validation folds).

Saves the model to models/hierarchy_linker_v1.json plus a small JSON
metadata sidecar with feature names and ranked importances.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

import numpy as np
import xgboost as xgb
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold

from feature_extractor import FEATURE_NAMES


MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "hierarchy_linker_v1.json")
META_PATH = os.path.join(MODEL_DIR, "hierarchy_linker_v1.meta.json")


@dataclass
class FoldResult:
    fold: int
    auc: float
    aucpr: float
    precision_at_05: float
    recall_at_05: float
    f1_at_05: float
    best_iteration: int


def _xgb_params(scale_pos_weight: float) -> dict:
    return {
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


def _balanced_pos_weight(y: np.ndarray) -> float:
    """sqrt of imbalance ratio - avoids over-inflating positive scores
    while still nudging the model towards recall."""
    pos = max(int(y.sum()), 1)
    neg = max(int((y == 0).sum()), 1)
    return float(np.sqrt(neg / pos))


def cross_validate(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    n_splits: int = 5,
    num_boost_round: int = 500,
    early_stopping_rounds: int = 30,
    verbose: bool = False,
) -> list[FoldResult]:
    """Run GroupKFold CV and return per-fold metrics."""
    gkf = GroupKFold(n_splits=n_splits)
    results: list[FoldResult] = []

    scale_pos_weight = _balanced_pos_weight(y)

    for fold_i, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), start=1):
        dtrain = xgb.DMatrix(X[train_idx], label=y[train_idx], feature_names=FEATURE_NAMES)
        dval = xgb.DMatrix(X[val_idx], label=y[val_idx], feature_names=FEATURE_NAMES)

        booster = xgb.train(
            _xgb_params(scale_pos_weight),
            dtrain,
            num_boost_round=num_boost_round,
            evals=[(dval, "val")],
            early_stopping_rounds=early_stopping_rounds,
            verbose_eval=verbose,
        )

        best_iter = booster.best_iteration if booster.best_iteration is not None else (booster.num_boosted_rounds() - 1)
        scores = booster.predict(dval, iteration_range=(0, best_iter + 1))
        preds = (scores >= 0.5).astype(int)

        results.append(FoldResult(
            fold=fold_i,
            auc=roc_auc_score(y[val_idx], scores),
            aucpr=average_precision_score(y[val_idx], scores),
            precision_at_05=precision_score(y[val_idx], preds, zero_division=0),
            recall_at_05=recall_score(y[val_idx], preds, zero_division=0),
            f1_at_05=f1_score(y[val_idx], preds, zero_division=0),
            best_iteration=best_iter,
        ))
    return results


def train_final_model(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    num_boost_round: int = 500,
    early_stopping_rounds: int = 30,
    min_boost_round: int = 150,
) -> tuple[xgb.Booster, dict]:
    """
    Train a final model on all data. Uses one held-out group fold to pick
    the best iteration via early stopping, then refits on full data using
    max(best_iter + 1, min_boost_round) rounds so the model has enough
    capacity even when the validation fold is trivially separable.
    """
    pos = max(int(y.sum()), 1)
    neg = max(int((y == 0).sum()), 1)
    scale_pos_weight = _balanced_pos_weight(y)
    params = _xgb_params(scale_pos_weight)

    # Use one fold of GroupKFold to pick best_iter
    gkf = GroupKFold(n_splits=5)
    train_idx, val_idx = next(gkf.split(X, y, groups))

    dtrain = xgb.DMatrix(X[train_idx], label=y[train_idx], feature_names=FEATURE_NAMES)
    dval = xgb.DMatrix(X[val_idx], label=y[val_idx], feature_names=FEATURE_NAMES)

    booster = xgb.train(
        params,
        dtrain,
        num_boost_round=num_boost_round,
        evals=[(dval, "val")],
        early_stopping_rounds=early_stopping_rounds,
        verbose_eval=False,
    )
    best_iter = booster.best_iteration if booster.best_iteration is not None else (booster.num_boosted_rounds() - 1)
    final_rounds = max(int(best_iter) + 1, min_boost_round)

    # Refit on full data with the chosen iteration count
    dfull = xgb.DMatrix(X, label=y, feature_names=FEATURE_NAMES)
    final = xgb.train(
        params,
        dfull,
        num_boost_round=final_rounds,
        verbose_eval=False,
    )

    info = {
        "scale_pos_weight": scale_pos_weight,
        "best_iteration": int(best_iter),
        "num_boost_round": int(final_rounds),
        "params": params,
        "n_train": int(len(y)),
        "n_positives": int(y.sum()),
        "n_negatives": int((y == 0).sum()),
    }
    return final, info


def feature_importance(booster: xgb.Booster, top_n: Optional[int] = None) -> list[tuple[str, float]]:
    """Return ranked (feature, gain) tuples."""
    score = booster.get_score(importance_type="gain")
    # Pad with 0 for unseen features so the output is stable
    full = [(name, float(score.get(name, 0.0))) for name in FEATURE_NAMES]
    full.sort(key=lambda kv: kv[1], reverse=True)
    if top_n is not None:
        full = full[:top_n]
    return full


def save_model(booster: xgb.Booster, info: dict, importances: list[tuple[str, float]]) -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    booster.save_model(MODEL_PATH)
    meta = {
        "feature_names": FEATURE_NAMES,
        "training_info": info,
        "feature_importance": [{"feature": n, "gain": g} for n, g in importances],
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2, default=str)


def load_model() -> tuple[xgb.Booster, dict]:
    booster = xgb.Booster()
    booster.load_model(MODEL_PATH)
    with open(META_PATH) as f:
        meta = json.load(f)
    return booster, meta


if __name__ == "__main__":
    from synthetic_data import generate_corpus
    from training_data_builder import build_training_data, summarize_training_data

    print("=" * 70)
    print("Training XGBoost Hierarchy Linker")
    print("=" * 70)

    print("\n[1/4] Generating corpus...")
    corpus = generate_corpus(num_msas=60, seed=42)

    print("[2/4] Building training data...")
    X, y, groups, meta = build_training_data(
        corpus,
        hard_negatives_per_positive=5,
        easy_negatives_per_positive=2,
        seed=42,
    )
    stats = summarize_training_data(y, meta)
    print(f"  pairs: {stats['total_pairs']}, positives: {stats['positives']}, "
          f"negatives: {stats['negatives']}")

    print("[3/4] Cross-validating (GroupKFold, 5 splits)...")
    cv_results = cross_validate(X, y, groups, n_splits=5)
    for r in cv_results:
        print(f"  Fold {r.fold}: AUC={r.auc:.4f}  AUCPR={r.aucpr:.4f}  "
              f"P={r.precision_at_05:.3f}  R={r.recall_at_05:.3f}  F1={r.f1_at_05:.3f}  "
              f"best_iter={r.best_iteration}")
    print(f"  Mean AUC:   {np.mean([r.auc for r in cv_results]):.4f}")
    print(f"  Mean AUCPR: {np.mean([r.aucpr for r in cv_results]):.4f}")
    print(f"  Mean F1:    {np.mean([r.f1_at_05 for r in cv_results]):.4f}")

    print("\n[4/4] Training final model on full data...")
    booster, info = train_final_model(X, y, groups)
    importances = feature_importance(booster)
    save_model(booster, info, importances)
    print(f"  Saved model -> {MODEL_PATH}")
    print(f"  Saved meta  -> {META_PATH}")

    print("\nTop 10 features by gain:")
    for name, gain in importances[:10]:
        print(f"  {name:30s} {gain:.3f}")
