import types

from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc


def _make_window(app, doc):
    win = object.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.nodes = {}
    win.id_to_node = {}
    win.edges = []
    win.NODE_RADIUS = 10
    win.canvas = types.SimpleNamespace(delete=lambda *a, **k: None)
    win.drawing_helper = types.SimpleNamespace(_fill_gradient_circle=lambda *a, **k: [])
    win._draw_node = lambda *a, **k: None
    win._draw_edge = lambda *a, **k: None
    win._place_table = lambda *a, **k: None
    win._update_scroll_region = lambda: None
    return win


def test_copy_paste_between_cbn_diagrams():
    doc1 = CausalBayesianNetworkDoc(name="d1")
    doc1.network.add_node("A", cpd=0.5)
    doc1.positions["A"] = (0, 0)
    doc1.types["A"] = "variable"
    app = types.SimpleNamespace(active_cbn=doc1, diagram_clipboard=None, diagram_clipboard_type=None)

    win1 = _make_window(app, doc1)
    snap1 = win1._clone_node_strategy1("A")
    snap2 = win1._clone_node_strategy2("A")
    snap3 = win1._clone_node_strategy3("A")
    snap4 = win1._clone_node_strategy4("A")
    assert snap1 == snap2 == snap3 == snap4

    win1.selected_node = "A"
    win1.copy_selected()
    assert app.diagram_clipboard == snap1
    assert app.diagram_clipboard_type == "Causal Bayesian Network"

    doc2 = CausalBayesianNetworkDoc(name="d2")
    app.active_cbn = doc2
    win2 = _make_window(app, doc2)

    for strat in (
        win2._reconstruct_node_strategy1,
        win2._reconstruct_node_strategy2,
        win2._reconstruct_node_strategy3,
        win2._reconstruct_node_strategy4,
    ):
        app.diagram_clipboard = snap1
        doc2.network.nodes.clear()
        doc2.network.parents.clear()
        doc2.network.cpds.clear()
        doc2.positions.clear()
        doc2.types.clear()
        name = strat(app.diagram_clipboard, doc2)
        assert name.startswith("A")
        assert name in doc2.network.nodes
        assert doc2.positions[name] == (doc1.positions["A"][0] + 20, doc1.positions["A"][1] + 20)
        assert doc2.network.cpds[name] is doc1.network.cpds["A"]
        assert doc2.network.parents[name] is doc1.network.parents["A"]

    doc2.network.nodes.clear()
    doc2.network.parents.clear()
    doc2.network.cpds.clear()
    doc2.positions.clear()
    doc2.types.clear()
    app.diagram_clipboard = snap1
    win2.paste_selected()
    assert "A" in doc2.network.nodes
    assert doc2.positions["A"] == (doc1.positions["A"][0] + 20, doc1.positions["A"][1] + 20)
    assert doc2.network.cpds["A"] is doc1.network.cpds["A"]
    assert doc2.network.parents["A"] is doc1.network.parents["A"]


def test_copy_paste_creates_clone_with_shared_data():
    doc = CausalBayesianNetworkDoc(name="d")
    doc.network.add_node("A", cpd=0.5)
    doc.network.add_node("B", parents=["A"], cpd={(True,): 0.9, (False,): 0.1})
    doc.positions["A"] = (0, 0)
    doc.positions["B"] = (0, 0)
    doc.types["A"] = doc.types["B"] = "variable"
    app = types.SimpleNamespace(active_cbn=doc, diagram_clipboard=None, diagram_clipboard_type=None)
    win = _make_window(app, doc)
    win.selected_node = "B"
    win.copy_selected()
    win.paste_selected()
    clones = [n for n in doc.network.nodes if n.startswith("B") and n != "B"]
    assert clones
    clone_name = clones[0]
    assert doc.network.cpds[clone_name] is doc.network.cpds["B"]
    assert doc.network.parents[clone_name] is doc.network.parents["B"]
    doc.network.cpds["B"][(True,)] = 0.8
    assert doc.network.cpds[clone_name][(True,)] == 0.8
