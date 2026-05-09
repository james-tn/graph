"""
End-to-End POC Orchestrator

Single entry point that:
  1. Generates a synthetic train+held-out corpus
  2. Builds pairwise training data (positives + hard/easy negatives)
  3. Cross-validates the XGBoost model with GroupKFold
  4. Trains a final model on all training pairs
  5. Evaluates XGBoost vs rule-based baseline on the held-out corpus
  6. Prints a one-page report and writes JSON results

Run:  python run_poc.py
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime

import numpy as np

from evaluate import evaluate, print_metrics, print_wins, print_losses
from feature_extractor import FEATURE_NAMES
from predict import HierarchyLinker
from synthetic_data import generate_corpus, corpus_stats
from train_model import (
    cross_validate,
    feature_importance,
    save_model,
    train_final_model,
)
from training_data_builder import build_training_data, summarize_training_data


REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")


def main() -> None:
    t0 = time.time()
    os.makedirs(REPORT_DIR, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORT_DIR, f"poc_report_{run_id}.json")

    print("=" * 72)
    print("Contract Hierarchy Linker - XGBoost POC")
    print("=" * 72)

    # ------------------------------------------------------------------
    # 1. Generate corpora
    # ------------------------------------------------------------------
    print("\n[Step 1/5] Generating synthetic corpora")
    train_corpus = generate_corpus(num_msas=60, seed=42)
    test_corpus = generate_corpus(num_msas=80, seed=999)
    train_stats = corpus_stats(train_corpus)
    test_stats = corpus_stats(test_corpus)
    print(f"  train: {train_stats['total_contracts']} contracts "
          f"({train_stats['child_contracts']} children)")
    print(f"  test:  {test_stats['total_contracts']} contracts "
          f"({test_stats['child_contracts']} children)")
    print(f"  test extraction quality: clean={test_stats['children_with_clean_ref']}  "
          f"corrupted={test_stats['children_with_corrupted_ref']}  "
          f"missing={test_stats['children_with_missing_ref']}")

    # ------------------------------------------------------------------
    # 2. Build training data
    # ------------------------------------------------------------------
    print("\n[Step 2/5] Building pairwise training data")
    X, y, groups, meta = build_training_data(
        train_corpus,
        hard_negatives_per_positive=5,
        easy_negatives_per_positive=2,
        seed=42,
    )
    train_data_stats = summarize_training_data(y, meta)
    print(f"  pairs: {train_data_stats['total_pairs']}  "
          f"(positives={train_data_stats['positives']}, "
          f"negatives={train_data_stats['negatives']})")
    print(f"  by_kind: {train_data_stats['by_kind']}")
    print(f"  features: {len(FEATURE_NAMES)}  "
          f"unique children (groups): {len(np.unique(groups))}")

    # ------------------------------------------------------------------
    # 3. Cross-validation
    # ------------------------------------------------------------------
    print("\n[Step 3/5] GroupKFold cross-validation (5 splits)")
    cv = cross_validate(X, y, groups, n_splits=5)
    for r in cv:
        print(f"  Fold {r.fold}: AUC={r.auc:.4f}  AUCPR={r.aucpr:.4f}  "
              f"F1@0.5={r.f1_at_05:.3f}  best_iter={r.best_iteration}")
    cv_aucpr = float(np.mean([r.aucpr for r in cv]))
    cv_auc = float(np.mean([r.auc for r in cv]))
    print(f"  Mean AUC:   {cv_auc:.4f}")
    print(f"  Mean AUCPR: {cv_aucpr:.4f}")

    # ------------------------------------------------------------------
    # 4. Final training
    # ------------------------------------------------------------------
    print("\n[Step 4/5] Training final model")
    booster, info = train_final_model(X, y, groups)
    importances = feature_importance(booster)
    save_model(booster, info, importances)
    print(f"  rounds: {info['num_boost_round']}  best_iter: {info['best_iteration']}")
    print(f"  scale_pos_weight: {info['scale_pos_weight']:.3f}")
    print("  Top 10 features:")
    for name, gain in importances[:10]:
        print(f"    {name:30s}  gain={gain:.2f}")

    # ------------------------------------------------------------------
    # 5. Evaluation: XGBoost vs rule-based on held-out corpus
    # ------------------------------------------------------------------
    print("\n[Step 5/5] Evaluating on held-out test corpus")
    linker = HierarchyLinker(booster, {
        "feature_names": FEATURE_NAMES,
        "feature_importance": [{"feature": n, "gain": g} for n, g in importances],
    })
    rule_m, xgb_m, rows = evaluate(test_corpus, linker, candidate_strategy="all_msas")

    print("\n--- Rule-based baseline ---")
    print_metrics(rule_m)

    print("\n--- XGBoost POC ---")
    print_metrics(xgb_m)

    print("\n--- Differential analysis ---")
    print_wins(rows, n=5)
    print_losses(rows, n=5)

    # ------------------------------------------------------------------
    # Save JSON report
    # ------------------------------------------------------------------
    report = {
        "run_id": run_id,
        "elapsed_sec": round(time.time() - t0, 2),
        "train_corpus_stats": train_stats,
        "test_corpus_stats": test_stats,
        "training_data_stats": train_data_stats,
        "cv_results": [
            {
                "fold": r.fold, "auc": r.auc, "aucpr": r.aucpr,
                "precision_at_05": r.precision_at_05,
                "recall_at_05": r.recall_at_05,
                "f1_at_05": r.f1_at_05,
                "best_iteration": r.best_iteration,
            } for r in cv
        ],
        "cv_mean_auc": cv_auc,
        "cv_mean_aucpr": cv_aucpr,
        "training_info": info,
        "top_features": [{"feature": n, "gain": g} for n, g in importances[:15]],
        "evaluation": {
            "rule_based": rule_m.to_dict(),
            "xgboost": xgb_m.to_dict(),
        },
        "wins": [r for r in rows if r["xgb_correct"] and not r["rule_correct"]][:20],
        "losses": [r for r in rows if not r["xgb_correct"]][:20],
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    delta_acc = xgb_m.accuracy - rule_m.accuracy
    delta_recall = xgb_m.recall - rule_m.recall
    print("\n" + "=" * 72)
    print("POC Summary")
    print("=" * 72)
    print(f"  Total elapsed:               {report['elapsed_sec']}s")
    print(f"  Rule-based accuracy:         {rule_m.accuracy:.4f}")
    print(f"  XGBoost accuracy:            {xgb_m.accuracy:.4f}")
    print(f"  Lift (accuracy):             +{delta_acc:.4f} ({delta_acc * 100:+.1f} pp)")
    print(f"  Rule-based recall:           {rule_m.recall:.4f}")
    print(f"  XGBoost recall:              {xgb_m.recall:.4f}")
    print(f"  Lift (recall):               +{delta_recall:.4f} ({delta_recall * 100:+.1f} pp)")
    print(f"  Children rescued by XGBoost: "
          f"{sum(1 for r in rows if r['xgb_correct'] and not r['rule_correct'])}")
    print(f"  Report saved:                {report_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
