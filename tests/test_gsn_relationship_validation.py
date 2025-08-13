import pytest
from gsn import GSNNode


def test_context_between_goals_disallowed():
    g1 = GSNNode("g1", "Goal")
    g2 = GSNNode("g2", "Goal")
    with pytest.raises(ValueError):
        g1.add_child(g2, relation="context")


def test_solved_with_context_child_disallowed():
    goal = GSNNode("g", "Goal")
    ctx = GSNNode("c", "Context")
    with pytest.raises(ValueError):
        goal.add_child(ctx, relation="solved")


def test_assumption_cannot_have_children():
    assump = GSNNode("a", "Assumption")
    goal = GSNNode("g", "Goal")
    with pytest.raises(ValueError):
        assump.add_child(goal)
