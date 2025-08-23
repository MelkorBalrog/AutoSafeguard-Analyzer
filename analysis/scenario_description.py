"""Utilities for generating scenario descriptions from parameters."""

from __future__ import annotations

from typing import Iterable, List, Tuple


def _phrase_trigger(
    sclass: str, oru: str, action: str, ocls: str, odds: str, tc: str, fi: str
) -> str:
    parts: List[str] = []
    if sclass:
        parts.append(f"In a {sclass} scenario")
    if tc:
        parts.append(f"when {tc}")
    if oru or action:
        oa = " ".join(p for p in [oru, action] if p).strip()
        parts.append(oa if parts else oa.capitalize())
    if ocls:
        seg = f"within {ocls}"
        seg += f" ({odds})" if odds else ""
        parts.append(seg)
    elif odds:
        parts.append(f"in {odds}")
    if fi:
        parts.append(f"leading to {fi}")
    return " ".join(parts) + "." if parts else ""


def _phrase_insufficiency(
    sclass: str, oru: str, action: str, ocls: str, odds: str, tc: str, fi: str
) -> str:
    parts: List[str] = []
    if fi:
        parts.append(fi.capitalize())
    if sclass:
        parts.append(f"in a {sclass} scenario")
    if oru or action:
        oa = " ".join(p for p in [oru, action] if p).strip()
        parts.append(f"as {oa}" if parts else oa.capitalize())
    if tc:
        parts.append(f"when {tc}")
    if ocls:
        seg = f"under {ocls}"
        seg += f" ({odds})" if odds else ""
        parts.append(seg)
    elif odds:
        parts.append(f"under {odds}")
    return " ".join(parts) + "." if parts else ""


def template_phrases(
    scenario_class: str,
    other_road_users: str,
    action: str,
    odd_elements: Iterable[Tuple[str, str]],
    triggering_condition: str,
    functional_insufficiency: str,
) -> List[str]:
    """Return two descriptive phrases for a scenario."""

    names = [n for n, _ in odd_elements if n]
    classes = sorted({c for _, c in odd_elements if c})
    odds = ", ".join(names)
    ocls = ", ".join(classes)
    p1 = _phrase_trigger(
        scenario_class,
        other_road_users,
        action,
        ocls,
        odds,
        triggering_condition,
        functional_insufficiency,
    )
    p2 = _phrase_insufficiency(
        scenario_class,
        other_road_users,
        action,
        ocls,
        odds,
        triggering_condition,
        functional_insufficiency,
    )
    return [p for p in (p1, p2) if p]
