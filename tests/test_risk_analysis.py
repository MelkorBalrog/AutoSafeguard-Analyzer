import types
from analysis.models import HazopDoc, HazopEntry, StpaDoc, StpaEntry, merge_malfunctions, compute_overall_impact, compute_cyber_risk_level


def test_merge_malfunctions():
    hz_entry = HazopEntry("f", "m1", "", "", "", "", True, "", False, "", "")
    hazop = HazopDoc("HZ", [hz_entry])
    st_entry = StpaEntry("a", "u1", "u2", "", "")
    stpa = StpaDoc("ST", "", [st_entry])
    result = merge_malfunctions([hazop], [stpa], ["HZ"], ["ST"])
    assert sorted(result) == ["m1", "u1", "u2"]


def test_cyber_risk_level():
    overall = compute_overall_impact("Moderate", "Major", "Negligible", "Negligible")
    risk = compute_cyber_risk_level(overall, "High")
    assert overall == "Major"
    assert risk == "Critical"
