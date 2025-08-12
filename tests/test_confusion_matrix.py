import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.confusion_matrix import compute_metrics, compute_counts


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


def test_compute_counts_basic():
    counts = compute_counts(50, 10, 30, 10)
    assert math.isclose(counts["tp"], 50)
    assert math.isclose(counts["fp"], 10)
    assert math.isclose(counts["tn"], 30)
    assert math.isclose(counts["fn"], 10)
    assert math.isclose(counts["p"], 60)
    assert math.isclose(counts["n"], 40)


def test_compute_counts_auto_fp():
    counts = compute_counts(hours=100, validation_target=0.01, p=60, n=40, target_type="fp")
    assert math.isclose(counts["fp"], 0.01 * 100)
    assert math.isclose(counts["tn"], 40 - 0.01 * 100)
    assert math.isclose(counts["tp"], 60)
    assert math.isclose(counts["fn"], 0.0)
    assert math.isclose(counts["p"], 60)
    assert math.isclose(counts["n"], 40)


def test_compute_counts_auto_fn():
    counts = compute_counts(hours=100, validation_target=0.02, p=60, n=40, target_type="fn")
    assert math.isclose(counts["fn"], 0.02 * 100)
    assert math.isclose(counts["tp"], 60 - 0.02 * 100)
    assert math.isclose(counts["tn"], 40)
    assert math.isclose(counts["fp"], 0.0)


def test_compute_counts_auto_tp():
    counts = compute_counts(hours=100, validation_target=0.5, p=60, n=40, target_type="tp")
    assert math.isclose(counts["tp"], 0.5 * 100)
    assert math.isclose(counts["fn"], 60 - 0.5 * 100)
    assert math.isclose(counts["tn"], 40)
    assert math.isclose(counts["fp"], 0.0)


def test_compute_counts_auto_tn():
    counts = compute_counts(hours=100, validation_target=0.2, p=60, n=40, target_type="tn")
    assert math.isclose(counts["tn"], 0.2 * 100)
    assert math.isclose(counts["fp"], 40 - 0.2 * 100)
    assert math.isclose(counts["tp"], 60)
    assert math.isclose(counts["fn"], 0.0)


def test_compute_counts_zero_hours():
    counts = compute_counts(hours=0, validation_target=0.1, p=10, n=10, target_type="fp")
    assert counts["tp"] == 10
    assert counts["tn"] == 10
    assert counts["fp"] == 0.0
    assert counts["fn"] == 0.0
