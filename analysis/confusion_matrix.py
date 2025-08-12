"""Confusion matrix utilities."""
from __future__ import annotations

from typing import Dict, Iterable, Tuple


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


def counts_from_validation(entries: Iterable[Tuple[float, float, float]]) -> Dict[str, float]:
    """Derive confusion matrix counts from validation results.

    Each entry is a tuple ``(result, target, acceptance)`` where ``result`` is
    the measured hazardous behaviour rate, ``target`` is the validation target
    and ``acceptance`` is the acceptance criterion.  The predicted class is
    determined by comparing ``result`` against ``target`` while the ground truth
    uses ``acceptance``.

    Parameters
    ----------
    entries:
        Iterable of ``(result, target, acceptance)`` values.

    Returns
    -------
    dict
        Dictionary with keys ``tp``, ``fp``, ``tn`` and ``fn``.
    """

    counts = {"tp": 0.0, "fp": 0.0, "tn": 0.0, "fn": 0.0}
    for result, target, acceptance in entries:
        result = float(result)
        target = float(target)
        acceptance = float(acceptance)
        # Predicted positive if result exceeds the validation target.
        predicted_positive = result > target
        # Actual positive if result exceeds the acceptance criterion.
        actual_positive = result > acceptance
        if predicted_positive and actual_positive:
            counts["tp"] += 1
        elif predicted_positive and not actual_positive:
            counts["fp"] += 1
        elif not predicted_positive and actual_positive:
            counts["fn"] += 1
        else:
            counts["tn"] += 1
    return counts

