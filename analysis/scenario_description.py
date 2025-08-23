"""Utilities for generating scenario descriptions from parameters."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


EXCLUDED_PARAMS = {
    "recall",
    "accuracy",
    "precision",
    "presicion",
    "f1 score",
    "f1_score",
    "f1score",
    "f1",
}


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


def _normalize_params(params: Sequence[str]) -> List[str]:
    norm: List[str] = []
    for p in params:
        if isinstance(p, dict):
            items = p.items()
        elif isinstance(p, str) and p.startswith("{") and p.endswith("}"):
            try:
                from ast import literal_eval

                items = literal_eval(p).items()  # type: ignore[assignment]
            except Exception:
                items = [(p, "")]
        else:
            items = [(p, "")]
        for k, v in items:
            key = str(k).strip()
            if key.lower() in EXCLUDED_PARAMS:
                continue
            val = str(v).strip()
            norm.append(f"{key}: {val}" if val else key)
    return norm


def _build_odd_phrase(
    odd_elements: Iterable[Tuple[str, str, Sequence[str]]]
) -> str:
    env: List[Tuple[str, str]] = []
    infra: List[Tuple[str, str]] = []
    road: List[Tuple[str, str]] = []
    for name, cls, params in odd_elements:
        filtered = _normalize_params(params)
        plist = ", ".join(filtered)
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
    """Return a descriptive phrase for a scenario."""

    odd_phrase = _build_odd_phrase(odd_elements)
    phrase = _phrase_insufficiency(
        scenario_class,
        other_road_users,
        action,
        odd_phrase,
        triggering_condition,
        functional_insufficiency,
    )
    return [phrase] if phrase else []
