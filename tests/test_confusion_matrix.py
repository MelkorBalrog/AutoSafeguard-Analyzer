import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.confusion_matrix import (
    compute_metrics,
    compute_metrics_from_target,
    compute_rates,
)


def test_compute_metrics_basic():
    metrics = compute_metrics(50, 10, 30, 10)
    assert math.isclose(metrics["accuracy"], (50 + 30) / (50 + 10 + 30 + 10))
    assert math.isclose(metrics["precision"], 50 / (50 + 10))
    assert math.isclose(metrics["recall"], 50 / (50 + 10))
    prec = 50 / (50 + 10)
    rec = 50 / (50 + 10)
    expected_f1 = 2 * prec * rec / (prec + rec)
    assert math.isclose(metrics["f1"], expected_f1)


def test_compute_metrics_zero_division():
    metrics = compute_metrics(0, 0, 0, 0)
    assert metrics["accuracy"] == 0.0
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1"] == 0.0


def test_compute_rates_basic():
    counts = compute_rates(50, 10, 30, 10, 100, 0.01)
    assert math.isclose(counts["tp"], 50)
    assert math.isclose(counts["fp"], 10)
    assert math.isclose(counts["tn"], 30)
    assert math.isclose(counts["fn"], 10)
    assert math.isclose(counts["p"], 60)
    assert math.isclose(counts["n"], 40)


def test_compute_rates_auto_counts():
    counts = compute_rates(hours=100, validation_target=0.01, p=60, n=40)
    assert math.isclose(counts["fp"], 0.01 * 100)
    assert math.isclose(counts["fn"], 0.01 * 100)
    assert math.isclose(counts["tp"], 60 - 0.01 * 100)
    assert math.isclose(counts["tn"], 40 - 0.01 * 100)
    assert math.isclose(counts["p"], 60)
    assert math.isclose(counts["n"], 40)


def test_compute_rates_zero_hours():
    counts = compute_rates(0, 0, 0, 0, 0, None)
    assert counts["tp"] == 0.0
    assert counts["tn"] == 0.0
    assert counts["fp"] == 0.0
    assert counts["fn"] == 0.0


def test_compute_metrics_from_target():
    data = compute_metrics_from_target(hours=100, validation_target=0.01, p=60, n=40)
    assert math.isclose(data["accuracy"], 0.98)
    assert math.isclose(data["precision"], 0.9833333333333333)
    assert math.isclose(data["recall"], 0.9833333333333333)
    assert math.isclose(data["f1"], 0.9833333333333333)
    assert math.isclose(data["tp"], 59.0)
    assert math.isclose(data["fp"], 1.0)
    assert math.isclose(data["tn"], 39.0)
    assert math.isclose(data["fn"], 1.0)
    assert math.isclose(data["tp_rate"], 0.59)
    assert math.isclose(data["fp_rate"], 0.01)
    assert math.isclose(data["tn_rate"], 0.39)
    assert math.isclose(data["fn_rate"], 0.01)
