import types

from gsn import GSNNode, GSNDiagram
from gui.gsn_diagram_window import GSNDiagramWindow


def test_copy_paste_creates_clone():
    root = GSNNode("Root", "Goal")
    child = GSNNode("Child", "Goal")
    root.add_child(child)
    diag = GSNDiagram(root)

    app = types.SimpleNamespace(diagram_clipboard=None, diagram_clipboard_type=None)
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.app = app
    win.diagram = diag
    win.id_to_node = {child.unique_id: child}
    win.selected_node = child
    win.refresh = lambda: None

    win.copy_selected()
    assert app.diagram_clipboard is child

    app.sync_nodes_by_id = lambda n: setattr(n.original, "description", n.description)
    win.paste_selected()
    assert len(diag.nodes) == 2
    clone = diag.nodes[-1]
    assert clone.original is child.original
    clone.description = "updated"
    app.sync_nodes_by_id(clone)
    assert child.description == "updated"
