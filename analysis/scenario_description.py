"""Utilities for generating scenario descriptions from parameters."""

from __future__ import annotations

from typing import Iterable, List


def _phrase_trigger(
    oru: str, action: str, odds: str, tc: str, fi: str
) -> str:
    parts: List[str] = []
    if tc:
        parts.append(f"When {tc}")
    if oru or action:
        oa = " ".join(p for p in [oru, action] if p).strip()
        parts.append(oa if parts else oa.capitalize())
    if odds:
        parts.append(f"in {odds}")
    if fi:
        parts.append(f"leading to {fi}")
    return " ".join(parts) + "." if parts else ""


def _phrase_insufficiency(
    oru: str, action: str, odds: str, tc: str, fi: str
) -> str:
    parts: List[str] = []
    if fi:
        parts.append(fi.capitalize())
    if oru or action:
        oa = " ".join(p for p in [oru, action] if p).strip()
        parts.append(f"occurs as {oa}" if parts else oa.capitalize())
    if tc:
        parts.append(f"when {tc}")
    if odds:
        parts.append(f"under {odds}")
    return " ".join(parts) + "." if parts else ""


def template_phrases(
    other_road_users: str,
    action: str,
    odd_elements: Iterable[str],
    triggering_condition: str,
    functional_insufficiency: str,
) -> List[str]:
    """Return two descriptive phrases for a scenario."""

    odds = ", ".join(o for o in odd_elements if o) if odd_elements else ""
    p1 = _phrase_trigger(other_road_users, action, odds, triggering_condition, functional_insufficiency)
    p2 = _phrase_insufficiency(other_road_users, action, odds, triggering_condition, functional_insufficiency)
    return [p for p in (p1, p2) if p]
