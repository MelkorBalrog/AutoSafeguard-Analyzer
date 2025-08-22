import types

from gui.gsn_diagram_window import GSNDiagramWindow, GSNNode, GSNDiagram


def _make_window(app, diag):
    win = object.__new__(GSNDiagramWindow)
    win.app = app
    win.diagram = diag
    win.id_to_node = {n.unique_id: n for n in diag.nodes}
    win.canvas = types.SimpleNamespace(
        delete=lambda *a, **k: None,
        find_overlapping=lambda *a, **k: [],
        find_closest=lambda *a, **k: [],
        bbox=lambda *a, **k: None,
        gettags=lambda i: [],
    )
    win.refresh = lambda: None
    return win


def test_gsn_copy_paste_between_diagrams():
    root1 = GSNNode("A", "Goal", x=0, y=0)
    diag1 = GSNDiagram(root1)
    app = types.SimpleNamespace(diagram_clipboard=None, diagram_clipboard_type=None)
    win1 = _make_window(app, diag1)

    win1.selected_node = root1
    win1.copy_selected()
    assert app.diagram_clipboard is root1
    assert app.diagram_clipboard_type == "GSN"

    root2 = GSNNode("B", "Goal", x=0, y=0)
    diag2 = GSNDiagram(root2)
    win2 = _make_window(app, diag2)

    win2.paste_selected()
    assert len(diag2.nodes) == 2
    clone = diag2.nodes[1]
    assert clone.original is root1
