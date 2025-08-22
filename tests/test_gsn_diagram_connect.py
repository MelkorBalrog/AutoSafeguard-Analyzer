import pytest
from gsn import GSNNode, GSNDiagram


def test_connect_solved_relationship():
    parent = GSNNode("G", "Goal")
    child = GSNNode("S", "Solution")
    diag = GSNDiagram(parent)
    diag.connect(parent, child, relation="solved")
    assert child in parent.children
    assert child in diag.nodes


@pytest.mark.parametrize("typ", ["Context", "Assumption", "Justification"])
def test_connect_context_relationship(typ):
    parent = GSNNode("G", "Goal")
    child = GSNNode("C", typ)
    diag = GSNDiagram(parent)
    diag.connect(parent, child, relation="context")
    assert child in parent.context_children
    assert child in diag.nodes
