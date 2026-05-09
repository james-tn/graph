"""
Probability calibration for the hierarchy linker.

The XGBoost booster outputs scores in [0, 1] but those scores are not true
probabilities — they are biased by `scale_pos_weight` and the model's loss
shape. To make the AUTO_THRESHOLD=0.85 / REVIEW_THRESHOLD=0.60 decision
gates correspond to real precision / recall, we fit a small calibration
map post-hoc.

Two methods are supported:
    "platt"   : sigmoid(a*score + b), fit by logistic regression on
                out-of-fold scores. Two parameters, robust on small data.
    "isotonic": piecewise-constant non-decreasing map. More flexible but
                needs ~1000+ labels to be stable.

The chosen method is recorded in the meta JSON under "calibration":

    {
      "method": "platt",
      "platt": {"a": <float>, "b": <float>},
      "summary": {"n_samples": ..., "brier_before": ..., "brier_after": ...}
    }

`Calibrator.from_meta()` loads whatever was persisted and exposes
`Calibrator.transform(raw_scores)`. When meta has no calibration block
(legacy models), the calibrator is a no-op identity transform.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


def _clip_eps(p: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    return np.clip(p, eps, 1.0 - eps)


def _logit(p: np.ndarray) -> np.ndarray:
    p = _clip_eps(p)
    return np.log(p / (1.0 - p))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    # Numerically stable.
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    neg = ~pos
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[neg])
    out[neg] = ez / (1.0 + ez)
    return out


def fit_platt(
    raw_scores: np.ndarray,
    y_true: np.ndarray,
) -> tuple[float, float]:
    """Fit a Platt sigmoid `sigmoid(a*x + b)` via logistic regression on
    `logit(raw_scores)`.

    Why fit on logit(score) and not score directly: XGBoost predictions are
    already a sigmoid output, so the natural calibration variable is the
    pre-sigmoid log-odds.
    """
    from sklearn.linear_model import LogisticRegression

    raw_scores = np.asarray(raw_scores, dtype=float).reshape(-1)
    y_true = np.asarray(y_true, dtype=int).reshape(-1)

    if raw_scores.size == 0 or len(np.unique(y_true)) < 2:
        # Not enough info — identity calibration.
        return 1.0, 0.0

    z = _logit(raw_scores).reshape(-1, 1)
    # NB: do not use class_weight="balanced" here — Platt calibration is meant
    # to match the empirical base rate. Balancing the calibration step would
    # systematically over-shoot the prior on imbalanced data.
    lr = LogisticRegression(C=1.0, solver="lbfgs", max_iter=200)
    lr.fit(z, y_true)
    a = float(lr.coef_.ravel()[0])
    b = float(lr.intercept_.ravel()[0])
    return a, b


def apply_platt(raw_scores: np.ndarray, a: float, b: float) -> np.ndarray:
    raw_scores = np.asarray(raw_scores, dtype=float)
    return _sigmoid(a * _logit(raw_scores) + b)


def fit_isotonic(
    raw_scores: np.ndarray,
    y_true: np.ndarray,
) -> dict:
    """Fit an isotonic map (piecewise-constant). Returns a dict suitable
    for JSON serialization with `x_thresholds` and `y_values`.
    """
    from sklearn.isotonic import IsotonicRegression

    raw_scores = np.asarray(raw_scores, dtype=float).reshape(-1)
    y_true = np.asarray(y_true, dtype=int).reshape(-1)

    if raw_scores.size == 0 or len(np.unique(y_true)) < 2:
        return {"x_thresholds": [0.0, 1.0], "y_values": [0.0, 1.0]}

    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(raw_scores, y_true)
    return {
        "x_thresholds": [float(x) for x in iso.X_thresholds_.tolist()],
        "y_values": [float(y) for y in iso.y_thresholds_.tolist()],
    }


def apply_isotonic(raw_scores: np.ndarray, payload: dict) -> np.ndarray:
    raw_scores = np.asarray(raw_scores, dtype=float)
    xs = np.asarray(payload.get("x_thresholds", [0.0, 1.0]), dtype=float)
    ys = np.asarray(payload.get("y_values", [0.0, 1.0]), dtype=float)
    if xs.size < 2:
        return raw_scores.copy()
    # Piecewise-linear interpolation; clip to [0,1].
    out = np.interp(raw_scores, xs, ys)
    return np.clip(out, 0.0, 1.0)


def brier_score(p: np.ndarray, y: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    y = np.asarray(y, dtype=float)
    if p.size == 0:
        return 0.0
    return float(np.mean((p - y) ** 2))


@dataclass
class Calibrator:
    """Apply a previously-fit calibration map to raw booster outputs."""

    method: str = "none"
    platt_a: float = 1.0
    platt_b: float = 0.0
    isotonic: Optional[dict] = None

    @classmethod
    def from_meta(cls, meta: dict) -> "Calibrator":
        cal = meta.get("calibration") if isinstance(meta, dict) else None
        if not isinstance(cal, dict):
            return cls(method="none")
        method = str(cal.get("method", "none")).lower()
        if method == "platt":
            params = cal.get("platt") or {}
            return cls(
                method="platt",
                platt_a=float(params.get("a", 1.0)),
                platt_b=float(params.get("b", 0.0)),
            )
        if method == "isotonic":
            return cls(method="isotonic", isotonic=cal.get("isotonic") or None)
        return cls(method="none")

    def transform(self, raw_scores) -> np.ndarray:
        arr = np.asarray(raw_scores, dtype=float)
        if self.method == "platt":
            return apply_platt(arr, self.platt_a, self.platt_b)
        if self.method == "isotonic":
            return apply_isotonic(arr, self.isotonic or {})
        return arr.copy()

    def transform_one(self, raw_score: float) -> float:
        return float(self.transform(np.array([float(raw_score)]))[0])


def fit_calibration(
    method: str,
    raw_scores: np.ndarray,
    y_true: np.ndarray,
) -> dict:
    """Fit + return a JSON-serializable calibration block.

    Output shape:
        {
            "method": "platt" | "isotonic",
            "platt": {"a": ..., "b": ...},          # if method == "platt"
            "isotonic": {"x_thresholds": ..., ...}, # if method == "isotonic"
            "summary": {
                "n_samples": int,
                "brier_before": float,
                "brier_after": float
            }
        }
    """
    method = (method or "platt").lower()
    raw_scores = np.asarray(raw_scores, dtype=float)
    y_true = np.asarray(y_true, dtype=int)

    summary = {
        "n_samples": int(raw_scores.size),
        "brier_before": brier_score(raw_scores, y_true),
    }

    if method == "isotonic":
        iso = fit_isotonic(raw_scores, y_true)
        calibrated = apply_isotonic(raw_scores, iso)
        summary["brier_after"] = brier_score(calibrated, y_true)
        return {"method": "isotonic", "isotonic": iso, "summary": summary}

    # Default: Platt
    a, b = fit_platt(raw_scores, y_true)
    calibrated = apply_platt(raw_scores, a, b)
    summary["brier_after"] = brier_score(calibrated, y_true)
    return {
        "method": "platt",
        "platt": {"a": a, "b": b},
        "summary": summary,
    }
