import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.confusion_matrix import (
    compute_metrics,
    counts_from_metrics,
    counts_from_validation,
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


def test_counts_from_validation():
    entries = [
        (2e-5, 1e-5, 1e-6),  # TP
        (5e-7, 1e-5, 1e-6),  # TN
        (2e-5, 1e-6, 1e-4),  # FP
        (2e-5, 5e-5, 1e-6),  # FN
    ]
    counts = counts_from_validation(entries)
    assert counts == {"tp": 1.0, "tn": 1.0, "fp": 1.0, "fn": 1.0}


def test_counts_from_metrics_round_trip():
    counts = counts_from_metrics(0.9, 0.8, 0.7)
    metrics = compute_metrics(
        counts["tp"], counts["fp"], counts["tn"], counts["fn"]
    )
    assert math.isclose(metrics["accuracy"], 0.9, rel_tol=1e-6)
    assert math.isclose(metrics["precision"], 0.8, rel_tol=1e-6)
    assert math.isclose(metrics["recall"], 0.7, rel_tol=1e-6)
