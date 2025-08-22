from __future__ import annotations

"""Helpers for ensuring unique work product names across analyses.

This module provides multiple strategies for generating unique names.
Version 4 represents the most feature complete approach and is the one used
throughout the application. Earlier versions are retained for regression
purposes.
"""

from typing import Iterable, Set, Any

from gsn import GSNModule
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc


def _collect_gsn_diagrams(module: GSNModule, ignore: Any) -> Set[str]:
    names: Set[str] = set()
    for diag in module.diagrams:
        if diag is not ignore:
            names.add(diag.root.user_name)
    for sub in module.modules:
        names.update(_collect_gsn_diagrams(sub, ignore))
    return names


def collect_work_product_names(app: Any, ignore: Any | None = None) -> Set[str]:
    """Return names of all known GSN and Bayesian network documents."""
    names: Set[str] = set()
    for diag in getattr(app, "gsn_diagrams", []):
        if diag is not ignore:
            names.add(diag.root.user_name)
    for mod in getattr(app, "gsn_modules", []):
        names.update(_collect_gsn_diagrams(mod, ignore))
    for doc in getattr(app, "cbn_docs", []):
        if doc is not ignore:
            names.add(doc.name)
    return names


def unique_name_v1(name: str, existing: Iterable[str]) -> str:
    """Append ``_n`` suffix until ``name`` is unique."""
    if name not in existing:
        return name
    idx = 1
    candidate = f"{name}_{idx}"
    while candidate in existing:
        idx += 1
        candidate = f"{name}_{idx}"
    return candidate


def unique_name_v2(name: str, existing: Iterable[str]) -> str:
    """Append ``-n`` suffix until ``name`` is unique."""
    if name not in existing:
        return name
    idx = 1
    candidate = f"{name}-{idx}"
    while candidate in existing:
        idx += 1
        candidate = f"{name}-{idx}"
    return candidate


def unique_name_v3(name: str, existing: Iterable[str]) -> str:
    """Append space and number until ``name`` is unique."""
    if name not in existing:
        return name
    idx = 1
    candidate = f"{name} {idx}"
    while candidate in existing:
        idx += 1
        candidate = f"{name} {idx}"
    return candidate


def unique_name_v4(name: str, existing: Iterable[str]) -> str:
    """Append ``(n)`` suffix until ``name`` is unique."""
    if name not in existing:
        return name
    idx = 1
    candidate = f"{name} ({idx})"
    while candidate in existing:
        idx += 1
        candidate = f"{name} ({idx})"
    return candidate
