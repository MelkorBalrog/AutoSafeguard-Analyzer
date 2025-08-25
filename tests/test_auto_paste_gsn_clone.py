import types

from mainappsrc.models.gsn import GSNNode, GSNDiagram
from AutoML import AutoMLApp, AutoML_Helper
from gui.controls import messagebox


def test_paste_node_creates_clone():
    root = GSNNode("Root", "Goal")
    child = GSNNode("Child", "Goal")
    root.add_child(child)
    diag = GSNDiagram(root)
    app = AutoMLApp.__new__(AutoMLApp)
    app.root_node = root
    app.top_events = []
    app.clipboard_node = child
    app.selected_node = root
    app.analysis_tree = types.SimpleNamespace(selection=lambda: [], item=lambda *a, **k: {})
    app.cut_mode = False
    app.update_views = lambda: None
    app._find_gsn_diagram = lambda n: diag
    AutoML_Helper.calculate_assurance_recursive = lambda *a, **k: None
    messagebox.showinfo = lambda *a, **k: None
    app.paste_node()
    assert len(root.children) == 2
    clone = root.children[-1]
    assert clone is not child
    assert clone.original is child
    assert not clone.is_primary_instance
    assert clone in diag.nodes
