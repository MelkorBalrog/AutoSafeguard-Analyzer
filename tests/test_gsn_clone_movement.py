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


def test_moving_gsn_original_preserves_clone_position():
    root = GSNNode("A", "Goal", x=0, y=0)
    clone = root.clone()
    clone.x = 50
    clone.y = 60
    diag = GSNDiagram(root)
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

    root.x += 100
    root.y += 100
    AutoMLApp.move_subtree(app, root, 100, 100)
    AutoMLApp.sync_nodes_by_id(app, root)

    assert (clone.x, clone.y) == (50, 60)
    assert (root.x, root.y) == (100, 100)


def test_moving_parent_with_clone_child_keeps_clone_static():
    root = GSNNode("A", "Goal", x=0, y=0)
    clone = root.clone(root)
    clone.x = 50
    clone.y = 60
    diag = GSNDiagram(root)
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

    root.x += 10
    root.y += 20
    AutoMLApp.move_subtree(app, root, 10, 20)
    AutoMLApp.sync_nodes_by_id(app, root)

    assert (root.x, root.y) == (10, 20)
    assert (clone.x, clone.y) == (50, 60)
