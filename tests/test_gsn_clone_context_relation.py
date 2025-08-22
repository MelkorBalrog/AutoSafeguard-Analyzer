import pytest
from gsn.nodes import GSNNode

@pytest.mark.parametrize("node_type", ["Context", "Assumption", "Justification"])
def test_clone_uses_context_relation(node_type):
    parent = GSNNode("P", "Goal")
    node = GSNNode("C", node_type)
    clone = node.clone(parent)
    assert clone in parent.context_children
    assert clone in parent.children
