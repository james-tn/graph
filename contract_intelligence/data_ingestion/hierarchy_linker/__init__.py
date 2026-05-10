"""
Contract Hierarchy Linker

Production module for ML-assisted parent-child contract linking.

Wraps the trained XGBoost model from `poc_xgboost_linker/` with:
  - Database-backed candidate generation (real contracts from PostgreSQL)
  - A `link_contract` orchestrator that runs the rule-based linker first
    and falls back to ML scoring + a review queue
  - Stable feature contract reused across training, evaluation, and inference

Public API:
    from data_ingestion.hierarchy_linker import (
        HierarchyLinker,
        LinkDecision,
        link_contract,
    )
"""

from .calibration import Calibrator, fit_calibration
from .feature_extractor import FEATURE_NAMES, build_idf_cache, extract_features
from .linker import HierarchyLinker, LinkDecision, LinkResult, link_contract

__all__ = [
    "Calibrator",
    "FEATURE_NAMES",
    "HierarchyLinker",
    "LinkDecision",
    "LinkResult",
    "build_idf_cache",
    "extract_features",
    "fit_calibration",
    "link_contract",
]
