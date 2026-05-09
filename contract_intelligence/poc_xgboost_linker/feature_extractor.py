"""
Pairwise Feature Extractor for Contract Hierarchy Linking

Given a (child, candidate_parent) pair, produces a numeric feature vector
that an XGBoost model can use to predict P(is_parent_child).

Feature categories:
  - Text matching: explicit reference matches, title overlap, amendment language
  - Party overlap: shared party counts, ratios
  - Temporal: date gaps, ordering, term overlap
  - Structural: contract-type compatibility, governing law / currency match
  - Semantic: title and document similarity (using cheap TF-IDF for the POC,
    drop-in replacement for real embeddings in production)
  - Metadata: contract type one-hots
"""

from __future__ import annotations

import math
import re
from datetime import date
from difflib import SequenceMatcher
from typing import Any

import numpy as np


# -- Feature schema (kept deterministic so XGBoost sees the same column order) --

FEATURE_NAMES: list[str] = [
    # Text matching
    "explicit_ref_exact",          # 1.0 if parent reference appears verbatim in child text or extracted_ref
    "explicit_ref_fuzzy",          # SequenceMatcher ratio between extracted_parent_reference and parent.reference_number
    "title_jaccard",               # Jaccard similarity of title tokens
    "title_substring",             # 1.0 if parent title is a substring of child title
    "amendment_language",          # 1.0 if child text contains "amends", "pursuant to", etc.
    # Party overlap
    "shared_parties_count",
    "shared_parties_ratio",
    "all_child_parties_in_parent",
    "client_match",
    "vendor_match",
    # Temporal
    "days_between_effective",      # NaN if either date missing
    "parent_precedes_child",       # 1.0 if parent.effective_date < child.effective_date
    "child_within_parent_term",    # 1.0 if child.effective_date is in parent's [effective, expiration]
    "log_days_gap",                # log1p(abs(days_between_effective)) bucketed
    # Structural
    "type_compatible",             # 1.0 if (parent_type, child_type) is a valid hierarchy
    "governing_law_match",
    "currency_match",
    "child_value_lt_parent",       # 1.0 if child total_value < parent total_value (typical for SOW under MSA)
    "value_ratio",                 # child_value / parent_value, NaN if either missing
    # Semantic
    "title_tfidf_cosine",          # TF-IDF cosine of titles
    "doc_tfidf_cosine",            # TF-IDF cosine of full text
    # Metadata one-hots (parent type)
    "parent_is_msa",
    "parent_is_sow",
    "parent_is_amendment",
    "parent_is_addendum",
    "parent_is_workorder",
    # Metadata one-hots (child type)
    "child_is_msa",
    "child_is_sow",
    "child_is_amendment",
    "child_is_addendum",
    "child_is_workorder",
    # Status
    "parent_is_terminated",
]


# -- Hierarchy compatibility rules --
# What contract types can be parents of what?

VALID_HIERARCHY: dict[str, set[str]] = {
    "MSA": {"SOW", "Amendment", "Addendum", "WorkOrder"},
    "SOW": {"Amendment", "WorkOrder", "Addendum"},
    "Contract": {"Amendment", "Addendum"},
}


def _safe_str(value: Any) -> str:
    return (value or "").strip()


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if len(t) > 2]


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / max(len(sa | sb), 1)


def _tfidf_cosine(text_a: str, text_b: str, idf_cache: dict[str, float]) -> float:
    """
    Lightweight TF-IDF cosine without scikit-learn dependency.
    For the POC this is a stand-in for proper embedding similarity.
    """
    toks_a = _tokenize(text_a)
    toks_b = _tokenize(text_b)
    if not toks_a or not toks_b:
        return 0.0

    def _vec(tokens: list[str]) -> dict[str, float]:
        counts: dict[str, float] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0.0) + 1.0
        # tf-idf style weighting using cached idf
        for t in list(counts.keys()):
            counts[t] = counts[t] * idf_cache.get(t, 1.0)
        return counts

    va = _vec(toks_a)
    vb = _vec(toks_b)

    # cosine
    common = set(va.keys()) & set(vb.keys())
    dot = sum(va[t] * vb[t] for t in common)
    norm_a = math.sqrt(sum(v * v for v in va.values()))
    norm_b = math.sqrt(sum(v * v for v in vb.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def build_idf_cache(corpus_texts: list[str]) -> dict[str, float]:
    """Build IDF cache once for the entire corpus (stand-in for real embeddings)."""
    df: dict[str, int] = {}
    n_docs = len(corpus_texts) or 1
    for text in corpus_texts:
        for tok in set(_tokenize(text)):
            df[tok] = df.get(tok, 0) + 1
    return {tok: math.log((1 + n_docs) / (1 + cnt)) + 1.0 for tok, cnt in df.items()}


def _amendment_language_score(text: str) -> float:
    """1.0 if the text contains language strongly suggesting it amends a parent."""
    text_lower = (text or "").lower()
    keywords = (
        "pursuant to", "amends", "modifies", "supplements",
        "executed under", "issued under", "appended to",
        "supersedes", "in connection with", "subordinate to",
    )
    return 1.0 if any(k in text_lower for k in keywords) else 0.0


def _ref_in_text(child_text: str, parent_ref: str) -> bool:
    """Check whether parent's reference number appears (loosely) in child text."""
    if not parent_ref:
        return False
    # Direct substring match
    if parent_ref.lower() in (child_text or "").lower():
        return True
    # Stripped/normalized comparison (drop punctuation)
    norm_ref = re.sub(r"[^a-zA-Z0-9]", "", parent_ref).lower()
    norm_text = re.sub(r"[^a-zA-Z0-9]", "", child_text or "").lower()
    return norm_ref in norm_text and len(norm_ref) >= 6


def _ref_fuzzy_score(extracted_ref: str | None, parent_ref: str) -> float:
    """How close is the extracted reference to the candidate parent's reference?"""
    if not extracted_ref or not parent_ref:
        return 0.0

    # Normalize both for comparison
    a = re.sub(r"[^a-zA-Z0-9]", "", extracted_ref).lower()
    b = re.sub(r"[^a-zA-Z0-9]", "", parent_ref).lower()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def extract_features(
    child: dict,
    parent: dict,
    idf_cache: dict[str, float],
) -> dict[str, float]:
    """
    Build the full feature dict for a (child, parent) pair.
    Inputs are dicts with the same keys as SyntheticContract.to_dict().
    """
    f: dict[str, float] = {name: 0.0 for name in FEATURE_NAMES}

    # ---- Text matching ----
    parent_ref = _safe_str(parent.get("reference_number"))
    extracted_ref = parent.get("reference_number") and child.get("extracted_parent_reference")

    f["explicit_ref_exact"] = float(_ref_in_text(_safe_str(child.get("full_text")), parent_ref))
    f["explicit_ref_fuzzy"] = _ref_fuzzy_score(child.get("extracted_parent_reference"), parent_ref)

    child_title = _safe_str(child.get("title"))
    parent_title = _safe_str(parent.get("title"))
    f["title_jaccard"] = _jaccard(_tokenize(child_title), _tokenize(parent_title))
    f["title_substring"] = float(parent_title.lower() in child_title.lower() and len(parent_title) > 5)
    f["amendment_language"] = _amendment_language_score(_safe_str(child.get("full_text")))

    # ---- Party overlap ----
    child_parties = {_safe_str(p.get("canonical_name")) for p in (child.get("parties") or [])}
    parent_parties = {_safe_str(p.get("canonical_name")) for p in (parent.get("parties") or [])}
    child_parties.discard("")
    parent_parties.discard("")

    shared = child_parties & parent_parties
    union = child_parties | parent_parties
    f["shared_parties_count"] = float(len(shared))
    f["shared_parties_ratio"] = len(shared) / max(len(union), 1)
    f["all_child_parties_in_parent"] = float(child_parties.issubset(parent_parties) and len(child_parties) > 0)

    def _role_match(role: str) -> bool:
        c = {p["canonical_name"] for p in (child.get("parties") or []) if p.get("role") == role}
        p_set = {p["canonical_name"] for p in (parent.get("parties") or []) if p.get("role") == role}
        return bool(c & p_set)

    f["client_match"] = float(_role_match("Client"))
    f["vendor_match"] = float(_role_match("Vendor"))

    # ---- Temporal ----
    c_eff = child.get("effective_date")
    p_eff = parent.get("effective_date")
    p_exp = parent.get("expiration_date")

    if isinstance(c_eff, date) and isinstance(p_eff, date):
        gap = (c_eff - p_eff).days
        f["days_between_effective"] = float(gap)
        f["parent_precedes_child"] = float(gap > 0)
        f["log_days_gap"] = math.log1p(abs(gap))
        within = gap >= 0 and (p_exp is None or c_eff <= p_exp)
        f["child_within_parent_term"] = float(within)
    else:
        # XGBoost handles NaN natively — much better than 0 for "missing"
        f["days_between_effective"] = float("nan")
        f["parent_precedes_child"] = float("nan")
        f["log_days_gap"] = float("nan")
        f["child_within_parent_term"] = float("nan")

    # ---- Structural ----
    parent_type = _safe_str(parent.get("contract_type"))
    child_type = _safe_str(child.get("contract_type"))

    f["type_compatible"] = float(child_type in VALID_HIERARCHY.get(parent_type, set()))
    f["governing_law_match"] = float(
        _safe_str(child.get("governing_law")) == _safe_str(parent.get("governing_law"))
        and bool(child.get("governing_law"))
    )
    f["currency_match"] = float(
        _safe_str(child.get("currency")) == _safe_str(parent.get("currency"))
        and bool(child.get("currency"))
    )

    cv = child.get("total_value")
    pv = parent.get("total_value")
    if isinstance(cv, (int, float)) and isinstance(pv, (int, float)) and pv > 0:
        f["child_value_lt_parent"] = float(cv < pv)
        f["value_ratio"] = float(cv) / float(pv)
    else:
        f["child_value_lt_parent"] = float("nan")
        f["value_ratio"] = float("nan")

    # ---- Semantic (TF-IDF cosine as embedding stand-in) ----
    f["title_tfidf_cosine"] = _tfidf_cosine(child_title, parent_title, idf_cache)
    f["doc_tfidf_cosine"] = _tfidf_cosine(
        _safe_str(child.get("full_text")),
        _safe_str(parent.get("full_text")),
        idf_cache,
    )

    # ---- Metadata one-hots ----
    type_map = {
        "MSA": "msa", "SOW": "sow", "Amendment": "amendment",
        "Addendum": "addendum", "WorkOrder": "workorder",
    }
    pt_key = type_map.get(parent_type)
    ct_key = type_map.get(child_type)
    if pt_key:
        f[f"parent_is_{pt_key}"] = 1.0
    if ct_key:
        f[f"child_is_{ct_key}"] = 1.0

    # ---- Status ----
    f["parent_is_terminated"] = float(_safe_str(parent.get("status")) == "terminated")

    return f


def features_to_array(features: dict[str, float]) -> np.ndarray:
    """Convert feature dict to a deterministic-order numpy array."""
    return np.array([features[name] for name in FEATURE_NAMES], dtype=np.float64)


if __name__ == "__main__":
    # Quick sanity check
    from synthetic_data import generate_corpus

    corpus = generate_corpus(num_msas=10, seed=42)
    idf = build_idf_cache([c.full_text for c in corpus])

    child = next(c for c in corpus if c.true_parent_id is not None)
    true_parent = next(c for c in corpus if c.id == child.true_parent_id)
    random_parent = next(c for c in corpus if c.contract_type == "MSA" and c.id != true_parent.id)

    print("=" * 70)
    print(f"Child: {child.contract_identifier} ({child.contract_type})")
    print(f"True parent: {true_parent.contract_identifier}")
    print("=" * 70)

    print("\n--- Features vs TRUE parent ---")
    feats_true = extract_features(child.to_dict(), true_parent.to_dict(), idf)
    for k, v in feats_true.items():
        print(f"  {k}: {v:.4f}")

    print("\n--- Features vs RANDOM parent ---")
    feats_rand = extract_features(child.to_dict(), random_parent.to_dict(), idf)
    for k, v in feats_rand.items():
        print(f"  {k}: {v:.4f}")
