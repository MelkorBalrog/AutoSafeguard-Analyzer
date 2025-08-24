import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from mainappsrc.models.gsn.nodes import GSNNode


@pytest.mark.parametrize("typ", ["Context", "Assumption", "Justification"])
def test_clone_uses_context_relationship(typ):
    parent = GSNNode("G", "Goal")
    node = GSNNode("N", typ)
    parent.add_child(node, relation="context")
    clone = node.clone(parent)
    assert clone in parent.context_children
