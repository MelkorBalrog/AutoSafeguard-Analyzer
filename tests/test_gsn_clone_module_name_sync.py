from gsn import GSNNode, GSNDiagram


def test_clone_displays_original_parent_module_name():
    parent_a = GSNNode("ModuleA", "Module")
    original = GSNNode("Goal", "Goal")
    parent_a.add_child(original)

    clone = original.clone()
    parent_b = GSNNode("ModuleB", "Module")
    parent_b.add_child(clone)

    diag = GSNDiagram(parent_a)
    diag.add_node(clone)
    diag.add_node(parent_b)

    assert diag._find_module_name(clone) == "ModuleA"

    parent_a.user_name = "Renamed"
    assert diag._find_module_name(clone) == "Renamed"
