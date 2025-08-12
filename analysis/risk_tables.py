"""Risk level and CAL determination utilities."""
from __future__ import annotations

from typing import Optional

# Mapping of attack feasibility and impact severity to overall risk level
RISK_LEVEL_TABLE = {
    ("High", "Severe"): "High",
    ("High", "Major"): "High",
    ("High", "Moderate"): "Medium",
    ("High", "Negligible"): "Low",
    ("Medium", "Severe"): "High",
    ("Medium", "Major"): "Medium",
    ("Medium", "Moderate"): "Low",
    ("Medium", "Negligible"): "Low",
    ("Low", "Severe"): "Medium",
    ("Low", "Major"): "Low",
    ("Low", "Moderate"): "Low",
    ("Low", "Negligible"): "Low",
}

# Mapping of impact severity and attack vector category to CAL level
CAL_TABLE = {
    ("Severe", "Physical-Local"): "CAL2",
    ("Severe", "Adjacent Network"): "CAL3",
    ("Severe", "Network-Remote"): "CAL4",
    ("Major", "Physical-Local"): "CAL1",
    ("Major", "Adjacent Network"): "CAL2",
    ("Major", "Network-Remote"): "CAL3",
    ("Moderate", "Physical-Local"): "CAL1",
    ("Moderate", "Adjacent Network"): "CAL1",
    ("Moderate", "Network-Remote"): "CAL2",
    # Negligible entries intentionally omitted – no CAL assigned
}

# Group mapping for detailed attack vectors to CAL table columns
_VECTOR_GROUP = {
    "Physical": "Physical-Local",
    "Local": "Physical-Local",
    "Adjacent": "Adjacent Network",
    "Network": "Network-Remote",
}


def determine_risk_level(feasibility: str, impact: str) -> str:
    """Return the overall risk level for the given feasibility and impact.

    Raises:
        ValueError: If the inputs are not recognised.
    """
    key = (feasibility, impact)
    if key not in RISK_LEVEL_TABLE:
        raise ValueError(f"Unsupported combination: {key}")
    return RISK_LEVEL_TABLE[key]


def determine_cal(impact: str, attack_vector: str) -> Optional[str]:
    """Return the CAL for the given impact and attack vector.

    ``None`` is returned when the impact is negligible or the combination is
    not defined in :data:`CAL_TABLE`.
    """
    if impact == "Negligible":
        return None
    group = _VECTOR_GROUP.get(attack_vector)
    if not group:
        return None
    return CAL_TABLE.get((impact, group))
