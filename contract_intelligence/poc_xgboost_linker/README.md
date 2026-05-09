# 🎯 POC: XGBoost Contract Hierarchy Linker

> **Proof-of-concept for ML-based contract parent-child detection using pairwise classification**

## What This POC Proves

Traditional contract hierarchy detection relies on:
- **Exact reference matching** (`reference_number = 'MSA-2023-001'`) → fails when references are missing/wrong
- **LLM judgment** → slow, expensive, inconsistent
- **Rule-based heuristics** → brittle, can't combine signals

This POC demonstrates an **XGBoost pairwise classification** approach that:
1. Combines **30+ engineered features** (text, semantic, temporal, structural)
2. Trains on **distantly-supervised** examples (existing parent-child links + hard negatives)
3. Outputs **calibrated probabilities** for human-in-the-loop review
4. Provides **feature importance** explanations for auditability

## How It Works

```
[New Child Contract]
        │
        ▼
[Candidate Generation]   ← Pre-filter to ~10-20 plausible parents
        │                  (same parties, compatible types, valid dates)
        ▼
[Feature Extraction]     ← 30+ features per (child, parent) pair
        │
        ▼
[XGBoost Classifier]     ← P(is_parent) for each candidate
        │
        ▼
[Decision Logic]
    ├─ prob ≥ 0.85 → AUTO-LINK
    ├─ prob ≥ 0.60 → FLAG for review
    └─ prob < 0.60 → No link
```

## Files

| File | Purpose |
|------|---------|
| `synthetic_data.py` | Generates realistic synthetic contract corpus for the POC |
| `feature_extractor.py` | Extracts 30+ features from (child, parent) pairs |
| `training_data_builder.py` | Builds positives + hard negatives + easy negatives |
| `train_model.py` | Trains XGBoost with evaluation metrics |
| `predict.py` | Inference engine with feature importance explanations |
| `evaluate.py` | Compares XGBoost vs rule-based baseline |
| `run_poc.py` | End-to-end orchestrator (run this first) |

## Quick Start

```powershell
# Install dependencies (xgboost, scikit-learn, pandas, numpy)
pip install -r requirements.txt

# Run the full POC end-to-end
python run_poc.py
```

The POC will:
1. Generate ~500 synthetic contracts (MSAs + SOWs + Amendments)
2. Build pairwise training data (~3000 pairs, mostly negatives)
3. Train XGBoost with cross-validation
4. Evaluate vs. rule-based baseline
5. Print results, confusion matrix, feature importance, and example predictions

## Expected Results

The XGBoost model should significantly outperform the rule-based baseline on:
- **Recall**: Catches relationships even when references are missing
- **Precision**: Reduces false positives by combining multiple weak signals
- **Robustness**: Handles noisy/dirty data gracefully (NaN-aware splits)

## Actual POC Results

Latest end-to-end run (`python run_poc.py`):

| Linker | Accuracy | Precision | Recall | F1 |
|--------|---------:|----------:|-------:|---:|
| Rule-based (exact `reference_number` match) | **60.5%** | 100% | 60.5% | 0.754 |
| **XGBoost** (32 features, 150 boost rounds) | **100.0%** | 100% | 100% | **1.000** |

Breakdown by extraction quality on the held-out test corpus (352 child contracts):

| Bucket | n | Rule-based correct | **XGBoost correct** |
|---|---:|---:|---:|
| Clean reference (LLM extracted it cleanly) | 213 | 213 | 213 |
| Corrupted reference (case/separator/typo drift) | 85 | 0 | **85** |
| Missing reference (LLM missed it entirely) | 54 | 0 | **54** |

**139 child contracts rescued** by XGBoost that the rule-based linker drops on the floor (corrupted + missing reference cases). Cross-validated AUCPR = 1.0 with `GroupKFold(5)` to prevent child-leakage between train/val.

Top features by gain:

1. `shared_parties_ratio` (143.1)
2. `title_tfidf_cosine` (114.3)
3. `explicit_ref_fuzzy` (54.6)
4. `parent_is_msa` (52.3)
5. `shared_parties_count` (49.1)
6. `parent_is_sow` (43.4)
7. `currency_match` (17.0)
8. `title_jaccard` (16.3)
9. `governing_law_match` (13.5)
10. `child_within_parent_term` (12.8)

Each run drops a JSON report under `reports/poc_report_<timestamp>.json` (full per-child predictions, fold metrics, feature importances) and a model artifact under `models/hierarchy_linker_v1.json`.

> ⚠️ Caveat: the synthetic corpus is solvable - it's not a calibration of real-world accuracy. The POC's job is to (1) prove the feature set and pipeline are sound and (2) quantify the lift over the rule-based fallback when references are noisy. Real-world numbers will be lower; the next step is to backfill labels from the production database (`contract_relationships` table) and retrain.

## Production Integration

After the POC, the model can be integrated into the ingestion pipeline:

```python
from poc_xgboost_linker.predict import HierarchyLinker

linker = HierarchyLinker.load("models/hierarchy_linker_v1.json")

# In postgres_ingestion.py, after extracting metadata:
result = linker.predict_parent(
    child_contract=new_contract,
    candidates=candidate_parents_from_db,
)

if result['decision'] == 'auto_link':
    insert_relationship(child_id, result['parent_id'])
elif result['decision'] == 'human_review':
    flag_for_review(child_id, result['top_candidates'])
```
