"""Utilities for generating scenario descriptions from parameters."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


def _phrase_trigger(
    sclass: str, oru: str, action: str, odd_phrase: str, tc: str, fi: str
) -> str:
    parts: List[str] = []
    if sclass:
        parts.append(f"In a {sclass} scenario")
    if tc:
        parts.append(f"when {tc}")
    if oru or action:
        oa = " ".join(p for p in [oru, action] if p).strip()
        parts.append(oa if parts else oa.capitalize())
    if odd_phrase:
        parts.append(odd_phrase)
    if fi:
        parts.append(f"leading to {fi}")
    return " ".join(parts) + "." if parts else ""


def _phrase_insufficiency(
    sclass: str, oru: str, action: str, odd_phrase: str, tc: str, fi: str
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
    if odd_phrase:
        parts.append(odd_phrase)
    return " ".join(parts) + "." if parts else ""


def _combine_segments(
    items: List[Tuple[str, str]], label: str, lead_word: str
) -> str:
    segs: List[str] = []
    for i, (name, params) in enumerate(items):
        start = lead_word if i == 0 else "and"
        seg = f"{start} {name} {label}"
        if params:
            seg += f", with {params} parameters"
        segs.append(seg)
    return "; ".join(segs)


def _build_odd_phrase(
    odd_elements: Iterable[Tuple[str, str, Sequence[str]]]
) -> str:
    env: List[Tuple[str, str]] = []
    infra: List[Tuple[str, str]] = []
    road: List[Tuple[str, str]] = []
    for name, cls, params in odd_elements:
        plist = ", ".join(p for p in params if p)
        if cls == "Environment":
            env.append((name, plist))
        elif cls == "Infrastructure":
            infra.append((name, plist))
        elif cls == "Road":
            road.append((name, plist))
    parts: List[str] = []
    if env:
        parts.append(_combine_segments(env, "Environment", "within"))
    if infra:
        parts.append(_combine_segments(infra, "Infrastructure", "on"))
    if road:
        parts.append(_combine_segments(road, "road", "within"))
    return ", ".join(parts)

def template_phrases(
    scenario_class: str,
    other_road_users: str,
    action: str,
    odd_elements: Iterable[Tuple[str, str, Sequence[str]]],
    triggering_condition: str,
    functional_insufficiency: str,
) -> List[str]:
    """Return two descriptive phrases for a scenario."""

    odd_phrase = _build_odd_phrase(odd_elements)
    p1 = _phrase_trigger(
        scenario_class,
        other_road_users,
        action,
        odd_phrase,
        triggering_condition,
        functional_insufficiency,
    )
    p2 = _phrase_insufficiency(
        scenario_class,
        other_road_users,
        action,
        odd_phrase,
        triggering_condition,
        functional_insufficiency,
    )
    return [p for p in (p1, p2) if p]
