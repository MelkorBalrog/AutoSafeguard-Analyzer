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
