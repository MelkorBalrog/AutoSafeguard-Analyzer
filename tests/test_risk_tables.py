import pytest

from analysis.risk_tables import determine_risk_level, determine_cal


def test_risk_level_table():
    assert determine_risk_level("High", "Severe") == "High"
    assert determine_risk_level("Medium", "Moderate") == "Low"
    assert determine_risk_level("Low", "Negligible") == "Low"


def test_cal_table():
    assert determine_cal("Severe", "Physical") == "CAL2"
    assert determine_cal("Severe", "Local") == "CAL2"
    assert determine_cal("Severe", "Adjacent") == "CAL3"
    assert determine_cal("Severe", "Network") == "CAL4"
    assert determine_cal("Moderate", "Network") == "CAL2"
    assert determine_cal("Negligible", "Network") is None


def test_invalid_combo():
    with pytest.raises(ValueError):
        determine_risk_level("Unknown", "Severe")
