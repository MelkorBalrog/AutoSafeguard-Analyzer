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

    snap1 = win1._clone_node_strategy1(root1)
    snap2 = win1._clone_node_strategy2(root1)
    snap3 = win1._clone_node_strategy3(root1)
    snap4 = win1._clone_node_strategy4(root1)
    assert snap1 is snap2 is snap3 is snap4 is root1

    win1.selected_node = root1
    win1.copy_selected()
    assert app.diagram_clipboard is snap1
    assert app.diagram_clipboard_type == "GSN"

    root2 = GSNNode("B", "Goal", x=0, y=0)
    diag2 = GSNDiagram(root2)
    win2 = _make_window(app, diag2)

    for strat in (
        win2._reconstruct_node_strategy1,
        win2._reconstruct_node_strategy2,
        win2._reconstruct_node_strategy3,
        win2._reconstruct_node_strategy4,
    ):
        app.diagram_clipboard = snap1
        node = strat(app.diagram_clipboard)
        assert node.x == root1.x + 20
        assert node.y == root1.y + 20
        assert node.original is root1

    app.diagram_clipboard = snap1
    win2.paste_selected()
    assert len(diag2.nodes) == 2
    new_node = next(n for n in diag2.nodes if n is not root2)
    assert new_node.original is root1
