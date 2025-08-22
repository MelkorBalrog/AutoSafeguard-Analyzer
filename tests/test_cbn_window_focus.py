import types
import weakref

from AutoML import AutoMLApp
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from gui.causal_bayesian_network_window import (
    CausalBayesianNetworkWindow,
    CBN_WINDOWS,
)


def _make_window(app, doc):
    win = CausalBayesianNetworkWindow.__new__(CausalBayesianNetworkWindow)
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
    win.focus_get = lambda: win if getattr(win, "has_focus", False) else None
    win.winfo_toplevel = lambda: win
    win._on_focus_in = types.MethodType(CausalBayesianNetworkWindow._on_focus_in, win)
    return win


def setup_app():
    app = AutoMLApp.__new__(AutoMLApp)
    app.diagram_clipboard = None
    app.diagram_clipboard_type = None
    app.selected_node = None
    app.root_node = None
    app.clipboard_node = None
    app.cut_mode = False
    doc1 = CausalBayesianNetworkDoc(name="d1")
    doc1.network.add_node("A", cpd=0.5)
    doc1.positions["A"] = [(0, 0)]
    doc1.types["A"] = "variable"
    doc2 = CausalBayesianNetworkDoc(name="d2")
    app.cbn_docs = [doc1, doc2]
    app.active_cbn = doc1
    win1 = _make_window(app, doc1)
    win2 = _make_window(app, doc2)
    CBN_WINDOWS.clear()
    CBN_WINDOWS.add(weakref.ref(win1))
    CBN_WINDOWS.add(weakref.ref(win2))
    return app, win1, win2, doc1, doc2


def test_cbn_window_strategies():
    app, win1, win2, _, _ = setup_app()
    app._cbn_window = win1
    win1.has_focus = True
    assert app._cbn_window_strategy1() is win1
    win1.has_focus = False
    win2.has_focus = True
    assert app._cbn_window_strategy2() is win2
    assert app._cbn_window_strategy3() is win1
    app._cbn_window = None
    win2.has_focus = False
    assert app._cbn_window_strategy4() in {win1, win2}


def test_cbn_paste_uses_focused_window():
    app, win1, win2, doc1, doc2 = setup_app()
    win1.selected_node = ("A", 0)
    win1._on_focus_in()
    app.copy_node()
    assert app.diagram_clipboard == (doc1, "A", 0)
    win1.has_focus = False
    win2.has_focus = True
    app.active_cbn = doc2
    win2._on_focus_in()
    app.paste_node()
    assert "A" in doc2.network.nodes
