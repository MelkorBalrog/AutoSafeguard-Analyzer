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


def test_cbn_copy_paste_shares_node_between_docs():
    doc1 = CausalBayesianNetworkDoc(name="d1")
    doc1.network.add_node("A", cpd=0.5)
    doc1.network.add_node("B", parents=["A"], cpd={(True,): 0.5, (False,): 0.1})
    doc1.positions["B"] = (0, 0)
    doc1.types["B"] = "variable"
    app = types.SimpleNamespace(
        active_cbn=doc1,
        cbn_docs=[doc1],
        diagram_clipboard=None,
        diagram_clipboard_type=None,
    )

    win1 = _make_window(app, doc1)

    snap1 = win1._clone_node_strategy1("B")
    snap2 = win1._clone_node_strategy2("B")
    snap3 = win1._clone_node_strategy3("B")
    snap4 = win1._clone_node_strategy4("B")
    assert snap1 == snap2 == snap3 == snap4 == (doc1, "B")

    win1.selected_node = "B"
    win1.copy_selected()
    assert app.diagram_clipboard == (doc1, "B")
    assert app.diagram_clipboard_type == "Causal Bayesian Network"

    doc2 = CausalBayesianNetworkDoc(name="d2")
    app.cbn_docs.append(doc2)
    app.active_cbn = doc2
    win2 = _make_window(app, doc2)

    for strat in (
        win2._reconstruct_node_strategy1,
        win2._reconstruct_node_strategy2,
        win2._reconstruct_node_strategy3,
        win2._reconstruct_node_strategy4,
    ):
        name = strat((doc1, "B"), doc2)
        assert name == "B"
        assert doc2.network.cpds["B"] is doc1.network.cpds["B"]

    win2.paste_selected()
    assert "B" in doc2.network.nodes
    assert doc2.network.cpds["B"] is doc1.network.cpds["B"]

    doc2.network.cpds["B"][(True,)] = 0.9
    assert doc1.network.cpds["B"][(True,)] == 0.9
