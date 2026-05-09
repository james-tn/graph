"""
Evaluation: XGBoost Linker vs Rule-Based Baseline

Compares two approaches on the same held-out corpus:

  Baseline (today): exact match on extracted_parent_reference == reference_number.
  XGBoost (POC):    predict_parent over a candidate set, applying thresholds.

Reports:
  - Overall accuracy, precision, recall, F1 on parent linkage
  - Breakdown by extraction quality (clean ref / corrupted ref / missing ref)
  - Sample of cases where XGBoost wins (rule-based fails to link)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from feature_extractor import build_idf_cache
from predict import HierarchyLinker
from synthetic_data import SyntheticContract


# ---------------------------------------------------------------------------
# Rule-based baseline: exact reference_number match against ingested contracts
# ---------------------------------------------------------------------------

def rule_based_predict(child: SyntheticContract, corpus: list[SyntheticContract]) -> Optional[int]:
    """Mirror the production rule-based linker (postgres_ingestion.py): exact
    match on extracted_parent_reference. Return parent_id if found."""
    ref = child.extracted_parent_reference
    if not ref:
        return None
    ref = ref.strip()
    if not ref:
        return None
    for cand in corpus:
        if cand.id == child.id:
            continue
        if cand.reference_number == ref:
            return cand.id
    return None


# ---------------------------------------------------------------------------
# Bucket children by the extraction-quality scenarios we care about
# ---------------------------------------------------------------------------

def _ref_bucket(child: SyntheticContract, corpus: list[SyntheticContract]) -> str:
    if child.extracted_parent_reference is None:
        return "missing_ref"
    if any(c.reference_number == child.extracted_parent_reference for c in corpus):
        return "clean_ref"
    return "corrupted_ref"


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

@dataclass
class LinkerMetrics:
    name: str
    n: int
    correct: int
    incorrect: int  # linked but to wrong parent
    no_link: int    # didn't link anything
    by_bucket: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def accuracy(self) -> float:
        return self.correct / self.n if self.n else 0.0

    @property
    def precision(self) -> float:
        # of the contracts where we returned a link, how many were correct
        linked = self.correct + self.incorrect
        return self.correct / linked if linked else 0.0

    @property
    def recall(self) -> float:
        # = accuracy here since every child has a true parent
        return self.accuracy

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "n": self.n,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "no_link": self.no_link,
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "by_bucket": self.by_bucket,
        }


def _empty_bucket() -> dict[str, int]:
    return {"n": 0, "correct": 0, "incorrect": 0, "no_link": 0}


def evaluate(
    corpus: list[SyntheticContract],
    linker: HierarchyLinker,
    candidate_strategy: str = "all_msas",
) -> tuple[LinkerMetrics, LinkerMetrics, list[dict]]:
    """
    Evaluate both linkers on every child in the corpus.

    candidate_strategy:
        "all_msas" - every MSA is a candidate (loose, realistic)
        "same_client" - filter to MSAs that share a client party

    Returns (rule_metrics, xgb_metrics, comparison_rows).
    """
    idf_cache = build_idf_cache([c.full_text for c in corpus] + [c.title for c in corpus])

    by_id = {c.id: c for c in corpus}
    children = [c for c in corpus if c.true_parent_id is not None]

    rule_m = LinkerMetrics(name="rule_based", n=0, correct=0, incorrect=0, no_link=0)
    xgb_m = LinkerMetrics(name="xgboost", n=0, correct=0, incorrect=0, no_link=0)
    for bucket in ("clean_ref", "corrupted_ref", "missing_ref"):
        rule_m.by_bucket[bucket] = _empty_bucket()
        xgb_m.by_bucket[bucket] = _empty_bucket()

    # Pre-build candidate lists once
    msa_dicts_by_id: dict[int, dict] = {}
    for c in corpus:
        if c.contract_type in ("MSA", "Contract"):
            msa_dicts_by_id[c.id] = c.to_dict()

    rows: list[dict] = []

    for child in children:
        bucket = _ref_bucket(child, corpus)
        true_parent_id = child.true_parent_id

        # ---- Rule-based ----
        rule_pred = rule_based_predict(child, corpus)

        # ---- XGBoost ----
        if candidate_strategy == "same_client":
            child_clients = {p["canonical_name"] for p in child.parties if p.get("role") == "Client"}
            cands = [
                d for d in msa_dicts_by_id.values()
                if d["id"] != child.id
                and any(p["canonical_name"] in child_clients for p in d["parties"])
            ]
        else:
            cands = [d for d in msa_dicts_by_id.values() if d["id"] != child.id]

        xgb_pred = linker.predict_parent(child.to_dict(), cands, idf_cache, top_k=3)

        # Score both
        for m, pred_id in [(rule_m, rule_pred), (xgb_m, xgb_pred.parent_id)]:
            m.n += 1
            m.by_bucket[bucket]["n"] += 1
            if pred_id is None:
                m.no_link += 1
                m.by_bucket[bucket]["no_link"] += 1
            elif pred_id == true_parent_id:
                m.correct += 1
                m.by_bucket[bucket]["correct"] += 1
            else:
                m.incorrect += 1
                m.by_bucket[bucket]["incorrect"] += 1

        rows.append({
            "child_id": child.id,
            "child_type": child.contract_type,
            "true_parent_id": true_parent_id,
            "bucket": bucket,
            "extracted_ref": child.extracted_parent_reference,
            "rule_predicted": rule_pred,
            "rule_correct": rule_pred == true_parent_id,
            "xgb_predicted": xgb_pred.parent_id,
            "xgb_decision": xgb_pred.decision,
            "xgb_confidence": round(xgb_pred.confidence, 4),
            "xgb_correct": xgb_pred.parent_id == true_parent_id,
        })

    return rule_m, xgb_m, rows


def print_metrics(m: LinkerMetrics) -> None:
    print(f"  {m.name:14s}  N={m.n}")
    print(f"    accuracy:   {m.accuracy:.4f}")
    print(f"    precision:  {m.precision:.4f}  (correct / linked)")
    print(f"    recall:     {m.recall:.4f}")
    print(f"    F1:         {m.f1:.4f}")
    print(f"    correct:    {m.correct}")
    print(f"    incorrect:  {m.incorrect}")
    print(f"    no_link:    {m.no_link}")
    print(f"    by extraction quality:")
    for bucket, vals in m.by_bucket.items():
        n = vals["n"] or 1
        print(f"      {bucket:14s}  n={vals['n']:4d}  correct={vals['correct']:4d}  "
              f"incorrect={vals['incorrect']:3d}  no_link={vals['no_link']:3d}  "
              f"acc={vals['correct']/n:.3f}")


def print_wins(rows: list[dict], n: int = 8) -> None:
    """Show cases where XGBoost gets it right but rule-based fails."""
    wins = [r for r in rows if r["xgb_correct"] and not r["rule_correct"]]
    print(f"\n  XGBoost wins (rule-based fails, XGBoost succeeds): {len(wins)}")
    for r in wins[:n]:
        print(f"    child {r['child_id']:4d} ({r['child_type']:9s})  "
              f"bucket={r['bucket']:14s}  "
              f"xgb_conf={r['xgb_confidence']:.3f}  "
              f"true_parent={r['true_parent_id']}  "
              f"extracted_ref={r['extracted_ref']!r}")


def print_losses(rows: list[dict], n: int = 4) -> None:
    """Show cases where XGBoost is wrong (for failure analysis)."""
    losses = [r for r in rows if not r["xgb_correct"]]
    print(f"\n  XGBoost failures: {len(losses)}")
    for r in losses[:n]:
        print(f"    child {r['child_id']:4d} ({r['child_type']:9s})  "
              f"bucket={r['bucket']:14s}  "
              f"decision={r['xgb_decision']}  "
              f"conf={r['xgb_confidence']:.3f}  "
              f"true={r['true_parent_id']}  predicted={r['xgb_predicted']}")


if __name__ == "__main__":
    from synthetic_data import generate_corpus

    print("Loading XGBoost linker...")
    linker = HierarchyLinker.from_disk()

    print("Generating held-out test corpus (different seed)...")
    corpus = generate_corpus(num_msas=80, seed=999)

    print(f"Evaluating {sum(1 for c in corpus if c.true_parent_id is not None)} child contracts...")
    rule_m, xgb_m, rows = evaluate(corpus, linker, candidate_strategy="all_msas")

    print("\n" + "=" * 70)
    print("Rule-Based Baseline")
    print("=" * 70)
    print_metrics(rule_m)

    print("\n" + "=" * 70)
    print("XGBoost Linker")
    print("=" * 70)
    print_metrics(xgb_m)

    print("\n" + "=" * 70)
    print("Differential Analysis")
    print("=" * 70)
    print_wins(rows)
    print_losses(rows)

    # Quick decision-distribution view
    decisions = Counter(r["xgb_decision"] for r in rows)
    print(f"\n  XGBoost decision distribution: {dict(decisions)}")
