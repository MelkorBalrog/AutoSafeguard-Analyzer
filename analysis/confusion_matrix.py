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


def compute_counts(
    tp: float | None = None,
    fp: float | None = None,
    tn: float | None = None,
    fn: float | None = None,
    *,
    hours: float = 0.0,
    validation_target: float | None = None,
    p: float | None = None,
    n: float | None = None,
    target_type: str = "fp",
) -> Dict[str, float]:
    """Derive confusion-matrix counts from dataset size and a target rate.

    The helper operates on explicit confusion-matrix counts (``tp``, ``fp``,
    ``tn``, ``fn``) or, when these are not provided, derives one of the counts
    from an allowed event rate (``validation_target``, in events/hour) over a
    mission duration ``hours``. The ``target_type`` argument indicates which
    confusion-matrix term the validation target represents (``"tp"``,
    ``"fp"``, ``"tn"`` or ``"fn"``).

    Parameters
    ----------
    tp, fp, tn, fn:
        Explicit confusion-matrix counts. If any are ``None`` then ``p`` and
        ``n`` must be provided so counts can be derived from the target rate.
    hours:
        Total test duration in hours (mission profile ``TAU ON``).
    validation_target:
        Allowed events per hour for the selected validation target.
    p, n:
        Dataset sizes for actual positives and negatives. Required when
        explicit confusion-matrix counts are not supplied.
    target_type:
        Which count the validation target constrains (``"tp"``, ``"fp"``,
        ``"tn"`` or ``"fn"``).

    Returns
    -------
    dict
        Dictionary containing the confusion-matrix counts (``tp``, ``fp``,
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
        count = rate * hours
        tt = target_type.lower()
        if tt not in {"tp", "fp", "tn", "fn"}:
            raise ValueError("target_type must be one of 'tp', 'fp', 'tn', 'fn'")
        tp = p
        tn = n
        fp = 0.0
        fn = 0.0
        if tt == "fp":
            fp = count
            tn = max(n - fp, 0.0)
        elif tt == "fn":
            fn = count
            tp = max(p - fn, 0.0)
        elif tt == "tp":
            tp = count
            fn = max(p - tp, 0.0)
        elif tt == "tn":
            tn = count
            fp = max(n - tn, 0.0)
    else:
        tp = float(tp)
        fp = float(fp)
        tn = float(tn)
        fn = float(fn)
        p = tp + fn
        n = tn + fp

    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "p": p, "n": n}


def compute_rates(
    tp: float | None = None,
    fp: float | None = None,
    tn: float | None = None,
    fn: float | None = None,
    *,
    hours: float = 0.0,
    validation_target: float | None = None,
    p: float | None = None,
    n: float | None = None,
    target_type: str = "fp",
) -> Dict[str, float]:
    """Compute confusion-matrix rates and per-hour limits.

    Parameters
    ----------
    tp, fp, tn, fn:
        Explicit confusion-matrix counts. If any are ``None`` then ``p`` and
        ``n`` must be provided so counts can be derived from the target rate.
    hours:
        Total test duration in hours (mission profile ``TAU ON``).
    validation_target:
        Allowed events per hour for the selected validation target.
    p, n:
        Dataset sizes for actual positives and negatives. Required when
        explicit confusion-matrix counts are not supplied.
    target_type:
        Which count the validation target constrains (``"tp"``, ``"fp"``,
        ``"tn"`` or ``"fn"``).

    Returns
    -------
    dict
        Dictionary containing counts, dataset totals and rate metrics:
        ``tpr``, ``tnr``, ``fpr`` and ``fnr``. Per-hour limits ``l_tp``,
        ``l_tn``, ``l_fp`` and ``l_fn`` are also included.
    """

    counts = compute_counts(
        tp,
        fp,
        tn,
        fn,
        hours=hours,
        validation_target=validation_target,
        p=p,
        n=n,
        target_type=target_type,
    )

    tp = counts["tp"]
    fp = counts["fp"]
    tn = counts["tn"]
    fn = counts["fn"]
    p = counts["p"]
    n = counts["n"]

    tpr = tp / p if p else 0.0
    tnr = tn / n if n else 0.0
    fpr = fp / n if n else 0.0
    fnr = fn / p if p else 0.0

    rate_tp = tp / hours if hours else 0.0
    rate_tn = tn / hours if hours else 0.0
    rate_fp = fp / hours if hours else 0.0
    rate_fn = fn / hours if hours else 0.0

    return {
        **counts,
        "tpr": tpr,
        "tnr": tnr,
        "fpr": fpr,
        "fnr": fnr,
        "l_tp": rate_tp,
        "l_tn": rate_tn,
        "l_fp": rate_fp,
        "l_fn": rate_fn,
    }
