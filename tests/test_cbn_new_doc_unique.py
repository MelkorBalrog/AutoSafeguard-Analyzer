import types

from tkinter import simpledialog
from gui.controls import messagebox
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc


def test_new_doc_rejects_duplicate_name(monkeypatch):
    app = types.SimpleNamespace(cbn_docs=[CausalBayesianNetworkDoc("Existing")])
    win = CausalBayesianNetworkWindow.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.toolbox = None
    win.refresh_docs = lambda: None
    win.doc_var = types.SimpleNamespace(set=lambda *a, **k: None)
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "Existing")
    called = {}
    monkeypatch.setattr(messagebox, "showwarning", lambda *a, **k: called.setdefault("warn", True))
    win.new_doc()
    assert called.get("warn")
    assert len(app.cbn_docs) == 1
