import types
from gsn import GSNNode, GSNDiagram
from AutoML import AutoMLApp


def test_moving_gsn_clone_preserves_original_position():
    root = GSNNode("A", "Goal", x=0, y=0)
    diag = GSNDiagram(root)
    clone = root.clone()
    clone.x = 50
    clone.y = 60
    diag.add_node(clone)
    root.display_label = ""
    clone.display_label = ""

    def get_all_nodes(self, _):
        return [root, clone]

    def get_all_fmea(self):
        return []

    app = object.__new__(AutoMLApp)
    app.root_node = root
    app.get_all_nodes = types.MethodType(get_all_nodes, app)
    app.get_all_fmea_entries = types.MethodType(get_all_fmea, app)

    # move clone
    clone.x += 100
    clone.y += 100
    AutoMLApp.sync_nodes_by_id(app, clone)

    assert (root.x, root.y) == (0, 0)
    assert (clone.x, clone.y) == (150, 160)


def test_moving_one_clone_does_not_shift_others():
    root = GSNNode("A", "Goal", x=0, y=0)
    diag = GSNDiagram(root)
    clone1 = root.clone()
    clone1.x, clone1.y = 10, 20
    clone2 = root.clone()
    clone2.x, clone2.y = 30, 40
    diag.add_node(clone1)
    diag.add_node(clone2)
    root.display_label = ""
    clone1.display_label = ""
    clone2.display_label = ""

    def get_all_nodes(self, _):
        return [root, clone1, clone2]

    def get_all_fmea(self):
        return []

    app = object.__new__(AutoMLApp)
    app.root_node = root
    app.get_all_nodes = types.MethodType(get_all_nodes, app)
    app.get_all_fmea_entries = types.MethodType(get_all_fmea, app)

    clone1.x += 5
    clone1.y += 5
    AutoMLApp.sync_nodes_by_id(app, clone1)

    assert (root.x, root.y) == (0, 0)
    assert (clone2.x, clone2.y) == (30, 40)