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


def test_clone_traverses_ancestors_for_module_name():
    root = GSNNode("ROOT", "Module")
    module = GSNNode("ModuleA", "Module")
    root.add_child(module)

    parent_goal = GSNNode("Parent", "Goal")
    module.add_child(parent_goal)

    original = GSNNode("Child", "Goal")
    parent_goal.add_child(original)

    clone = original.clone()
    other_module = GSNNode("Other", "Module")
    root.add_child(other_module)
    other_module.add_child(clone)

    diag = GSNDiagram(root)
    for n in [root, module, parent_goal, original, other_module, clone]:
        diag.add_node(n)

    assert diag._find_module_name(clone) == "ModuleA"
    module.user_name = "Renamed"
    assert diag._find_module_name(clone) == "Renamed"
