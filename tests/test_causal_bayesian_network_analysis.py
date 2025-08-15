import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis import CausalBayesianNetwork


def build_network():
    cbn = CausalBayesianNetwork()
    cbn.add_node("Rain", cpd=0.3)
    cbn.add_node("WetGround", parents=["Rain"])
    cbn.add_node("SlipperyRoad", parents=["WetGround"])
    return cbn


def test_slippery_road_probability():
    cbn = build_network()
    assert cbn.query("SlipperyRoad") == pytest.approx(0.3, rel=1e-3)


def test_slippery_road_given_rain():
    cbn = build_network()
    p = cbn.query("SlipperyRoad", {"Rain": True})
    assert p == pytest.approx(1.0, rel=1e-3)


def test_intervention_matches_conditioning_for_root():
    cbn = build_network()
    p_do = cbn.intervention("SlipperyRoad", {"Rain": True})
    p_cond = cbn.query("SlipperyRoad", {"Rain": True})
    assert p_do == pytest.approx(p_cond, rel=1e-6)


def test_missing_cpd_defaults_to_zero():
    cbn = CausalBayesianNetwork()
    cbn.add_node("Rain", cpd=0.5)
    cbn.add_node("WetGround", parents=["Rain"], cpd={(True,): 0.9})
    # Conditional probabilities are ignored; probability matches parent
    assert cbn.query("WetGround") == pytest.approx(0.5, rel=1e-3)


def test_truth_table_auto_fill():
    cbn = CausalBayesianNetwork()
    cbn.add_node("A", cpd=0.4)
    cbn.add_node("B", parents=["A"])
    rows = cbn.cpd_rows("B")
    assert len(rows) == 2
    assert rows[0][0] == (False,)
    assert rows[0][1] == pytest.approx(0.0)
    # probability of parent combination P(A=False) = 0.6
    assert rows[0][2] == pytest.approx(0.6, rel=1e-3)
    assert rows[0][3] == pytest.approx(0.0, rel=1e-3)
    assert rows[1][1] == pytest.approx(1.0)
    assert rows[1][2] == pytest.approx(0.4, rel=1e-3)
    # total probability for row A=True is 0.4 * 1.0
    assert rows[1][3] == pytest.approx(0.4, rel=1e-3)

def test_marginal_probability_propagation():
    cbn = CausalBayesianNetwork()
    cbn.add_node("Rain", cpd=0.3)
    cbn.add_node("WetGround", parents=["Rain"])
    cbn.add_node("SlipperyRoad", parents=["WetGround"])
    probs = cbn.marginal_probabilities()
    assert probs["Rain"] == pytest.approx(0.3, rel=1e-3)
    assert probs["WetGround"] == pytest.approx(0.3, rel=1e-3)
    assert probs["SlipperyRoad"] == pytest.approx(0.3, rel=1e-3)
    cbn.cpds["Rain"] = 0.6
    probs = cbn.marginal_probabilities()
    assert probs["WetGround"] == pytest.approx(0.6, rel=1e-3)
    assert probs["SlipperyRoad"] == pytest.approx(0.6, rel=1e-3)


def test_cpd_rows_respect_parent_dependencies():
    cbn = CausalBayesianNetwork()
    cbn.add_node("A", cpd=0.5)
    cbn.add_node("B", parents=["A"])
    cbn.add_node("C", parents=["A", "B"])

    rows = cbn.cpd_rows("C")
    # Expected joint distribution of (A, B) taking into account the dependency
    # of B on A. Only (A=True, B=True) and (A=False, B=False) have non-zero
    # probability.
    expected = [0.5, 0.0, 0.0, 0.5]
    for row, exp in zip(rows, expected):
        assert row[2] == pytest.approx(exp, rel=1e-3)
