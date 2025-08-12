import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.confusion_matrix import compute_metrics, compute_rates


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
    rates = compute_rates(50, 10, 30, 10, 100, 0.01)
    assert math.isclose(rates["tpr"], 50 / 60)
    assert math.isclose(rates["tnr"], 30 / 40)
    assert math.isclose(rates["fpr"], 10 / 40)
    assert math.isclose(rates["fnr"], 10 / 60)
    assert math.isclose(rates["tp_rate"], 50 / 100)
    assert math.isclose(rates["tn_rate"], 30 / 100)
    assert math.isclose(rates["fp_rate"], 10 / 100)
    assert math.isclose(rates["fn_rate"], 10 / 100)
    assert math.isclose(rates["fpr_max"], (0.01 * 100) / 40)
    assert math.isclose(rates["fnr_max"], (0.01 * 100) / 60)
    assert math.isclose(rates["tpr_min"], 1 - (0.01 * 100) / 60)
    assert math.isclose(rates["tnr_min"], 1 - (0.01 * 100) / 40)


def test_compute_rates_zero_hours():
    rates = compute_rates(0, 0, 0, 0, 0, None)
    assert rates["tp_rate"] == 0.0
    assert rates["tn_rate"] == 0.0
    assert rates["fp_rate"] == 0.0
    assert rates["fn_rate"] == 0.0
    assert rates["tpr"] == 0.0
    assert rates["tnr"] == 0.0
    assert rates["fpr"] == 0.0
    assert rates["fnr"] == 0.0
