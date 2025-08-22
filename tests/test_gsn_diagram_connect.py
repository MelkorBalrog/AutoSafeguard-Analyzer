import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gsn import GSNNode, GSNDiagram


def test_connect_adds_relationship_and_nodes():
    root = GSNNode("G1", "Goal")
    ctx = GSNNode("C1", "Context")
    diag = GSNDiagram(root)
    # Context node not added to diagram yet; connect should add and link
    diag.connect(root, ctx, relation="context")
    assert ctx in diag.nodes
    assert ctx in root.children
    assert ctx in root.context_children


def test_connect_solved_relationship():
    root = GSNNode("G1", "Goal")
    sol = GSNNode("S1", "Solution")
    diag = GSNDiagram(root)
    diag.connect(root, sol)
    assert sol in diag.nodes
    assert sol in root.children
    assert sol not in root.context_children
