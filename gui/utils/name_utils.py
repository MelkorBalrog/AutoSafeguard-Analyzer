from __future__ import annotations

"""Helpers for ensuring unique work product names across analyses.

This module provides multiple strategies for generating unique names.
Version 4 represents the most feature complete approach and is the one used
throughout the application. Earlier versions are retained for regression
purposes.
"""

from typing import Iterable, Set, Any

from mainappsrc.models.gsn import GSNModule


def _collect_gsn_diagrams(module: GSNModule, ignore: Any) -> Set[str]:
    names: Set[str] = set()
    for diag in module.diagrams:
        if diag is not ignore:
            names.add(diag.root.user_name)
    for sub in module.modules:
        names.update(_collect_gsn_diagrams(sub, ignore))
    return names


def collect_work_product_names_v1(app: Any, ignore: Any | None = None) -> Set[str]:
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

def collect_work_product_names_v2(app: Any, ignore: Any | None = None, diagram_type: str | None = None) -> Set[str]:
    if diagram_type == 'gsn':
        names: Set[str] = set()
        for diag in getattr(app, 'gsn_diagrams', []):
            if diag is not ignore:
                names.add(diag.root.user_name)
        for mod in getattr(app, 'gsn_modules', []):
            names.update(_collect_gsn_diagrams(mod, ignore))
        return names
    if diagram_type == 'cbn':
        names: Set[str] = set()
        for doc in getattr(app, 'cbn_docs', []):
            if doc is not ignore:
                names.add(doc.name)
        return names
    return collect_work_product_names_v1(app, ignore)

def collect_work_product_names_v3(app: Any, ignore: Any | None = None, diagram_type: str | None = None) -> Set[str]:
    names: Set[str] = set()
    if diagram_type in (None, 'gsn'):
        names.update(diag.root.user_name for diag in getattr(app, 'gsn_diagrams', []) if diag is not ignore)
        for mod in getattr(app, 'gsn_modules', []):
            names.update(_collect_gsn_diagrams(mod, ignore))
    if diagram_type in (None, 'cbn'):
        names.update(doc.name for doc in getattr(app, 'cbn_docs', []) if doc is not ignore)
    return names

def collect_work_product_names_v4(app: Any, ignore: Any | None = None, diagram_type: str | None = None) -> Set[str]:
    names: Set[str] = set()
    if diagram_type in (None, 'gsn'):
        for diag in getattr(app, 'gsn_diagrams', []):
            if diag is not ignore:
                names.add(diag.root.user_name)
        for mod in getattr(app, 'gsn_modules', []):
            names.update(_collect_gsn_diagrams(mod, ignore))
    if diagram_type in (None, 'cbn'):
        for doc in getattr(app, 'cbn_docs', []):
            if doc is not ignore:
                names.add(doc.name)
    return names

collect_work_product_names = collect_work_product_names_v4

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
