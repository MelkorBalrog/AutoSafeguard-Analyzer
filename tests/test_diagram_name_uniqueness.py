import types

from tkinter import simpledialog

from gui.gsn_explorer import GSNExplorer
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from gsn import GSNNode, GSNDiagram


def test_unique_gsn_diagram_names(monkeypatch):
    app = types.SimpleNamespace(gsn_diagrams=[], gsn_modules=[])
    root = GSNNode("A", "Goal")
    app.gsn_diagrams.append(GSNDiagram(root))
    explorer = GSNExplorer.__new__(GSNExplorer)
    explorer.app = app
    explorer.tree = types.SimpleNamespace(selection=lambda: ())
    explorer.item_map = {}
    explorer.populate = lambda: None

    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "A")

    explorer.new_diagram()
    assert len(app.gsn_diagrams) == 1


def test_unique_cbn_doc_names(monkeypatch):
    app = types.SimpleNamespace(cbn_docs=[CausalBayesianNetworkDoc(name="A")])
    win = CausalBayesianNetworkWindow.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.refresh_docs = lambda: None
    win.doc_var = types.SimpleNamespace(set=lambda v: None)

    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "A")

    win.new_doc()
    assert len(app.cbn_docs) == 1

