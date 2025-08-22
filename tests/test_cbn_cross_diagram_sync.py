import types

from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


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


def test_cross_diagram_clone_keeps_data_in_sync():
    doc1 = CausalBayesianNetworkDoc(name="d1")
    doc1.network.add_node("A", cpd=0.5)
    doc1.positions["A"] = [(0, 0)]
    doc1.types["A"] = "variable"
    app = types.SimpleNamespace(
        active_cbn=doc1,
        cbn_docs=[doc1],
        diagram_clipboard=None,
        diagram_clipboard_type=None,
    )
    win1 = _make_window(app, doc1)
    win1.selected_node = ("A", 0)
    win1.copy_selected()

    for strat in (
        win1._reconstruct_node_strategy1,
        win1._reconstruct_node_strategy2,
        win1._reconstruct_node_strategy3,
        win1._reconstruct_node_strategy4,
    ):
        doc2 = CausalBayesianNetworkDoc(name="d2")
        app.active_cbn = doc2
        if len(app.cbn_docs) == 1:
            app.cbn_docs.append(doc2)
        else:
            app.cbn_docs[1] = doc2
        win2 = _make_window(app, doc2)
        strat((doc1, "A", 0), doc2)
        assert doc2.network.cpds is doc1.network.cpds
        assert doc2.network.parents is doc1.network.parents
        assert doc2.network.nodes is doc1.network.nodes
        doc2.network.cpds["A"] = 0.8
        assert doc1.network.cpds["A"] == 0.8
        doc1.network.cpds["A"] = 0.3
        assert doc2.network.cpds["A"] == 0.3
        doc2.types["A"] = "Triggering Condition"
        assert doc1.types["A"] == "Triggering Condition"
        doc1.types["A"] = "variable"
        assert doc2.types["A"] == "variable"
        assert doc1.positions["A"][0] != doc2.positions["A"][0]

    doc3 = CausalBayesianNetworkDoc(name="d3")
    app.active_cbn = doc3
    app.cbn_docs.append(doc3)
    win3 = _make_window(app, doc3)
    win3.paste_selected()
    doc3.network.cpds["A"] = 0.6
    assert doc1.network.cpds["A"] == 0.6
    doc1.network.cpds["A"] = 0.1
    assert doc3.network.cpds["A"] == 0.1
