import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis import CausalBayesianNetwork


def build_network():
    cbn = CausalBayesianNetwork()
    cbn.add_node("Rain", cpd=0.3)
    cbn.add_node(
        "WetGround",
        parents=["Rain"],
        cpd={(True,): 0.9, (False,): 0.1},
    )
    cbn.add_node(
        "SlipperyRoad",
        parents=["WetGround"],
        cpd={(True,): 0.8, (False,): 0.05},
    )
    return cbn


def test_slippery_road_probability():
    cbn = build_network()
    assert cbn.query("SlipperyRoad") == pytest.approx(0.305, rel=1e-3)


def test_slippery_road_given_rain():
    cbn = build_network()
    p = cbn.query("SlipperyRoad", {"Rain": True})
    assert p == pytest.approx(0.725, rel=1e-3)


def test_intervention_matches_conditioning_for_root():
    cbn = build_network()
    p_do = cbn.intervention("SlipperyRoad", {"Rain": True})
    p_cond = cbn.query("SlipperyRoad", {"Rain": True})
    assert p_do == pytest.approx(p_cond, rel=1e-6)
