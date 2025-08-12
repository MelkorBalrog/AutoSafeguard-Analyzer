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
    """Derive confusion matrix counts from dataset size and limits.

    The helper operates on explicit confusion matrix counts (``tp``, ``fp``,
    ``tn``, ``fn``) or, when these are not provided, derives them from
    dataset sizes ``p`` and ``n`` together with an allowed hazardous event
    rate ``validation_target`` (events/hour) over a mission duration
    ``hours``.

    Parameters
    ----------
    tp, fp, tn, fn:
        Confusion matrix counts. If any are ``None`` then ``p`` and ``n``
        must be supplied and counts are derived assuming the per-hour limit
        ``validation_target`` applies equally to false positives and false
        negatives.
    hours:
        Total test duration in hours (mission profile ``TAU ON``).
    validation_target:
        Optional allowed hazardous events per hour for the selected
        validation target.
    p, n:
        Dataset sizes for actual positives and negatives. Required when
        explicit confusion matrix counts are not supplied.

    Returns
    -------
    dict
        Dictionary containing the confusion matrix counts (``tp``, ``fp``,
        ``tn``, ``fn``) and totals ``p`` and ``n``.
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

    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "p": p, "n": n}
