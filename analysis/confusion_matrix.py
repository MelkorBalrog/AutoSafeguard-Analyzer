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
    tp: float | None = None,
    fp: float | None = None,
    tn: float | None = None,
    fn: float | None = None,
    hours: float = 0.0,
    validation_target: float | None = None,
    p: float | None = None,
    n: float | None = None,
) -> Dict[str, float]:
    """Calculate confusion matrix rates and per-hour event rates.

    This helper can either operate on explicit confusion matrix counts
    (``tp``, ``fp``, ``tn``, ``fn``) or derive them from dataset sizes
    ``p`` (actual positives) and ``n`` (actual negatives) together with an
    allowed hazardous event rate ``validation_target`` expressed in
    events/hour.

    Parameters
    ----------
    tp, fp, tn, fn:
        Confusion matrix counts. If any are ``None`` then ``p`` and ``n``
        must be supplied and counts are derived assuming the per-hour
        limit ``validation_target`` applies equally to false positives and
        false negatives.
    hours:
        Total test duration in hours (mission profile ``TAU ON``).
    validation_target:
        Optional allowed hazardous events per hour for the selected
        validation target. When provided, additional maximum/minimum rates
        are computed using the formulas in the project documentation.
    p, n:
        Dataset sizes for actual positives and negatives. Required when
        explicit confusion matrix counts are not supplied.

    Returns
    -------
    dict
        Dictionary containing the confusion matrix counts (``tp``, ``fp``,
        ``tn``, ``fn``), derived totals ``p`` and ``n``, the dimensionless
        rates ``tpr``, ``tnr``, ``fpr`` and ``fnr`` as well as the per-hour
        event rates ``tp_rate``, ``tn_rate``, ``fp_rate`` and
        ``fn_rate``. When ``validation_target`` is supplied, the dictionary
        also contains ``fpr_max``, ``fnr_max``, ``tpr_min`` and
        ``tnr_min``.
    """

    hours = float(hours)
    if tp is None or fp is None or tn is None or fn is None:
        if p is None or n is None:
            raise ValueError(
                "Either confusion matrix counts or dataset sizes P and N must be provided"
            )
        p = float(p)
        n = float(n)
        rate = float(validation_target or 0.0)
        fp = rate * hours
        fn = rate * hours
        tp = max(p - fn, 0.0)
        tn = max(n - fp, 0.0)
    else:
        tp = float(tp)
        fp = float(fp)
        tn = float(tn)
        fn = float(fn)
        p = tp + fn
        n = tn + fp

    validation_target = float(validation_target) if validation_target is not None else None

    tpr = tp / p if p else 0.0
    tnr = tn / n if n else 0.0
    fpr = fp / n if n else 0.0
    fnr = fn / p if p else 0.0

    tp_rate = tp / hours if hours else 0.0
    tn_rate = tn / hours if hours else 0.0
    fp_rate = fp / hours if hours else 0.0
    fn_rate = fn / hours if hours else 0.0

    results = {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "p": p,
        "n": n,
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
