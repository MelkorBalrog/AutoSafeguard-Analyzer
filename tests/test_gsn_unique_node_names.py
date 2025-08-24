from mainappsrc.models.gsn.nodes import GSNNode
from mainappsrc.models.gsn.diagram import GSNDiagram

def test_gsn_unique_node_names():
    root = GSNNode("Goal", "Goal")
    diagram = GSNDiagram(root)
    # clone should retain name
    clone = root.clone()
    diagram.add_node(clone)
    assert clone.user_name == "Goal"
    # new nodes with same name should be renamed
    n1 = GSNNode("Goal", "Goal")
    diagram.add_node(n1)
    n2 = GSNNode("Goal", "Goal")
    diagram.add_node(n2)
    assert n1.user_name == "Goal_1"
    assert n2.user_name == "Goal_2"
