"""Confusion matrix utilities."""
from __future__ import annotations

from typing import Dict


def compute_metrics(tp: float, fp: float, tn: float, fn: float) -> Dict[str, float]:
    """Compute common classification metrics from confusion matrix counts.

    Parameters
    ----------
    tp, fp, tn, fn:
        True positives, false positives, true negatives and false negatives.

    Returns
    -------
    dict
        Dictionary with keys ``accuracy``, ``precision``, ``recall`` and ``f1``.
    """
    tp = float(tp)
    fp = float(fp)
    tn = float(tn)
    fn = float(fn)
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def compute_rates(
    tp: float,
    fp: float,
    tn: float,
    fn: float,
    hours: float,
    validation_target: float | None = None,
) -> Dict[str, float]:
    """Calculate confusion matrix rates and per-hour event rates.

    Parameters
    ----------
    tp, fp, tn, fn:
        Confusion matrix counts.
    hours:
        Total test duration in hours (mission profile ``TAU ON``).
    validation_target:
        Optional allowed hazardous events per hour for the selected
        validation target.  When provided, additional maximum/ minimum
        rates are computed using the formulas in the project documentation.

    Returns
    -------
    dict
        Dictionary with keys ``tpr``, ``tnr``, ``fpr``, ``fnr`` for the
        dimensionless rates as well as ``tp_rate``, ``tn_rate``, ``fp_rate``
        and ``fn_rate`` for the per-hour event rates.  When
        ``validation_target`` is supplied, the dictionary also contains
        ``fpr_max``, ``fnr_max``, ``tpr_min`` and ``tnr_min``.
    """

    tp = float(tp)
    fp = float(fp)
    tn = float(tn)
    fn = float(fn)
    hours = float(hours)
    validation_target = float(validation_target) if validation_target is not None else None

    p = tp + fn
    n = tn + fp

    tpr = tp / p if p else 0.0
    tnr = tn / n if n else 0.0
    fpr = fp / n if n else 0.0
    fnr = fn / p if p else 0.0

    tp_rate = tp / hours if hours else 0.0
    tn_rate = tn / hours if hours else 0.0
    fp_rate = fp / hours if hours else 0.0
    fn_rate = fn / hours if hours else 0.0

    results = {
        "tpr": tpr,
        "tnr": tnr,
        "fpr": fpr,
        "fnr": fnr,
        "tp_rate": tp_rate,
        "tn_rate": tn_rate,
        "fp_rate": fp_rate,
        "fn_rate": fn_rate,
    }

    if validation_target is not None and hours > 0.0:
        max_events = validation_target * hours
        fpr_max = max_events / n if n else 0.0
        fnr_max = max_events / p if p else 0.0
        results.update(
            {
                "fpr_max": fpr_max,
                "fnr_max": fnr_max,
                "tpr_min": 1.0 - fnr_max,
                "tnr_min": 1.0 - fpr_max,
            }
        )

    return results
