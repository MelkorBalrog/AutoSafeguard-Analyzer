import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.confusion_matrix import compute_metrics


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
