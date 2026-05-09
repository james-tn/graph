#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Active-learning loop: retrain the hierarchy linker from reviewer feedback.

This is a thin cron-friendly wrapper around `scripts/train_hierarchy_linker.py
--from-db`. It does three things:

  1. Counts positives (confirmed/rule_based/manual links) and labeled
     negatives (reviewer-rejected pairs) currently in the DB.
  2. If positives have grown by at least --min-new-positives since the last
     trained model (or no model exists), retrains.
  3. Always retrains if --force is passed.

Designed to run as a Container Apps Job, an Azure Function timer trigger,
or a plain cron entry once a day.

Usage:
    python scripts/retrain_from_reviews.py
    python scripts/retrain_from_reviews.py --force
    python scripts/retrain_from_reviews.py --min-new-positives 25
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "data_ingestion"))

META_PATH = (
    PROJECT_ROOT / "data_ingestion" / "hierarchy_linker" / "models"
    / "hierarchy_linker_v1.meta.json"
)


def _read_last_n_train() -> int:
    if not META_PATH.exists():
        return 0
    try:
        meta = json.loads(META_PATH.read_text())
        return int(meta.get("training_info", {}).get("n_positives", 0))
    except Exception:
        return 0


def _count_positives(cur, tenant_id: str = "default") -> int:
    cur.execute(
        """
        SELECT COUNT(*) AS n
        FROM contract_relationships
        WHERE tenant_id = %s
          AND parent_contract_id IS NOT NULL
          AND link_method = ANY(ARRAY['rule_based', 'ml_review_confirmed', 'manual'])
        """,
        (tenant_id,),
    )
    row = cur.fetchone()
    return int(row["n"] if isinstance(row, dict) else row[0])


def _count_rejected(cur, tenant_id: str = "default") -> int:
    cur.execute(
        """
        SELECT COUNT(*) AS n
        FROM link_review_queue
        WHERE tenant_id = %s
          AND status = 'rejected'
          AND candidate_parent_id IS NOT NULL
        """,
        (tenant_id,),
    )
    row = cur.fetchone()
    return int(row["n"] if isinstance(row, dict) else row[0])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tenant-id", default="default")
    parser.add_argument(
        "--min-new-positives", type=int, default=25,
        help="Skip retraining unless at least this many new positives exist "
             "since the last trained model.",
    )
    parser.add_argument("--force", action="store_true",
                        help="Retrain regardless of growth.")
    parser.add_argument(
        "--min-real-positives", type=int, default=200,
        help="If fewer real positives exist, the trainer falls back to the "
             "synthetic bootstrap corpus.",
    )
    args = parser.parse_args()

    from postgres_ingestion import get_db_connection

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            n_pos = _count_positives(cur, args.tenant_id)
            n_neg = _count_rejected(cur, args.tenant_id)
    finally:
        conn.close()

    last_n = _read_last_n_train()
    new_since_last = n_pos - last_n

    print(f"[retrain] positives in DB: {n_pos}")
    print(f"[retrain] reviewer-rejected pairs (labeled negatives): {n_neg}")
    print(f"[retrain] positives at last training: {last_n}")
    print(f"[retrain] new positives since last training: {new_since_last}")

    if not args.force and new_since_last < args.min_new_positives:
        print(f"[retrain] Skipping: < {args.min_new_positives} new positives.")
        return 0

    # Hand off to the main trainer with --from-db.
    print("[retrain] Running training...")
    from train_hierarchy_linker import (  # type: ignore  # noqa: E402
        build_real_training_data,
        train_and_save,
    )

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            X, y, groups, _meta = build_real_training_data(
                cur, tenant_id=args.tenant_id
            )
    finally:
        conn.close()

    n_real = int(y.sum()) if len(y) else 0
    if n_real < args.min_real_positives:
        # In production we don't ship the synthetic corpus, so don't try to
        # bootstrap. Leaving the existing model in place is the right call —
        # we'll retry on the next nightly run once more reviews pile up.
        try:
            from train_hierarchy_linker import build_synthetic_training_data  # type: ignore
            print(
                f"[retrain] Only {n_real} real positives; falling back to bootstrap."
            )
            X, y, groups, _meta = build_synthetic_training_data()
            train_and_save(X, y, groups, source="synthetic_bootstrap")
        except ImportError:
            print(
                f"[retrain] Only {n_real} real positives and bootstrap corpus not "
                f"available in this image; keeping existing model."
            )
            return 0
    else:
        train_and_save(X, y, groups, source="postgres")

    print("[retrain] Done.")
    return 0


if __name__ == "__main__":
    # Make sibling script importable without polluting global path order.
    sys.path.insert(0, str(Path(__file__).parent))
    sys.exit(main())
