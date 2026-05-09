"""
Unit tests for the probability calibration module.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_ingestion.hierarchy_linker.calibration import (  # noqa: E402
    Calibrator,
    apply_isotonic,
    apply_platt,
    brier_score,
    fit_calibration,
    fit_isotonic,
    fit_platt,
)


@pytest.fixture
def biased_scores():
    """Generate raw scores that systematically over-predict positives.

    Truth: y=1 with probability 0.3
    Raw scores: y=1 mean ~0.85, y=0 mean ~0.55  (over-confident model)
    """
    rng = np.random.default_rng(seed=42)
    n = 600
    y = (rng.random(n) < 0.3).astype(int)
    # Clip to (0,1) so logit is finite.
    raw = np.where(y == 1, rng.normal(0.85, 0.1, n), rng.normal(0.55, 0.15, n))
    raw = np.clip(raw, 0.02, 0.98)
    return raw, y


def test_calibrator_identity_when_no_meta():
    cal = Calibrator.from_meta({})
    arr = np.array([0.1, 0.5, 0.9])
    out = cal.transform(arr)
    np.testing.assert_array_almost_equal(out, arr)


def test_calibrator_identity_with_unknown_method():
    cal = Calibrator.from_meta({"calibration": {"method": "exotic"}})
    assert cal.method == "none"
    np.testing.assert_array_almost_equal(cal.transform([0.3, 0.7]), [0.3, 0.7])


def test_fit_platt_reduces_brier(biased_scores):
    raw, y = biased_scores
    a, b = fit_platt(raw, y)
    cal = apply_platt(raw, a, b)
    assert brier_score(cal, y) < brier_score(raw, y)
    # Calibrated mean should be much closer to base rate.
    assert abs(cal.mean() - y.mean()) < 0.05


def test_fit_isotonic_reduces_brier(biased_scores):
    raw, y = biased_scores
    iso = fit_isotonic(raw, y)
    cal = apply_isotonic(raw, iso)
    assert brier_score(cal, y) < brier_score(raw, y)


def test_fit_calibration_platt_meta_shape(biased_scores):
    raw, y = biased_scores
    block = fit_calibration("platt", raw, y)
    assert block["method"] == "platt"
    assert "a" in block["platt"]
    assert "b" in block["platt"]
    assert block["summary"]["n_samples"] == len(raw)
    assert block["summary"]["brier_after"] <= block["summary"]["brier_before"] + 1e-9


def test_fit_calibration_isotonic_meta_shape(biased_scores):
    raw, y = biased_scores
    block = fit_calibration("isotonic", raw, y)
    assert block["method"] == "isotonic"
    assert isinstance(block["isotonic"]["x_thresholds"], list)
    assert isinstance(block["isotonic"]["y_values"], list)
    assert block["summary"]["brier_after"] <= block["summary"]["brier_before"] + 1e-9


def test_calibrator_roundtrip_via_meta(biased_scores):
    raw, y = biased_scores
    block = fit_calibration("platt", raw, y)
    # Simulate persisting to JSON and loading back.
    meta = json.loads(json.dumps({"calibration": block}))
    cal = Calibrator.from_meta(meta)
    assert cal.method == "platt"
    cal_arr = cal.transform(raw)
    direct = apply_platt(raw, block["platt"]["a"], block["platt"]["b"])
    np.testing.assert_array_almost_equal(cal_arr, direct)


def test_calibrator_isotonic_roundtrip_via_meta(biased_scores):
    raw, y = biased_scores
    block = fit_calibration("isotonic", raw, y)
    meta = json.loads(json.dumps({"calibration": block}))
    cal = Calibrator.from_meta(meta)
    assert cal.method == "isotonic"
    cal_arr = cal.transform(raw)
    direct = apply_isotonic(raw, block["isotonic"])
    np.testing.assert_array_almost_equal(cal_arr, direct)


def test_calibrator_transform_one_scalar():
    block = {"method": "platt", "platt": {"a": 1.5, "b": -0.3}}
    cal = Calibrator.from_meta({"calibration": block})
    out = cal.transform_one(0.7)
    assert 0.0 <= out <= 1.0
    # Should match vector form.
    np.testing.assert_almost_equal(out, cal.transform(np.array([0.7]))[0])


def test_calibrator_handles_empty_input():
    cal = Calibrator(method="platt", platt_a=2.0, platt_b=0.5)
    out = cal.transform(np.array([]))
    assert out.shape == (0,)


def test_fit_platt_handles_single_class():
    """If all labels are 0, fit should fall back to identity (a=1, b=0)."""
    raw = np.array([0.1, 0.2, 0.3, 0.4])
    y = np.array([0, 0, 0, 0])
    a, b = fit_platt(raw, y)
    assert a == 1.0
    assert b == 0.0


def test_calibration_clips_to_unit_interval(biased_scores):
    raw, y = biased_scores
    block = fit_calibration("isotonic", raw, y)
    cal = Calibrator.from_meta({"calibration": block})
    out = cal.transform(np.array([0.0, 0.001, 0.5, 0.999, 1.0]))
    assert (out >= 0.0).all()
    assert (out <= 1.0).all()
