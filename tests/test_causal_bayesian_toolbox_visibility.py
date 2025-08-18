import types
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


class DummyVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, v):
        self.value = v


class DummyCB:
    def __init__(self):
        self.values = None

    def configure(self, **kw):
        if "values" in kw:
            self.values = kw["values"]

    def bind(self, *a, **k):
        pass


class DummyCanvas:
    def delete(self, *a, **k):
        pass


class DummyToolbox:
    def __init__(self):
        self.packed = False

    def pack(self, *a, **k):
        self.packed = True

    def pack_forget(self, *a, **k):
        self.packed = False

    def winfo_ismapped(self):
        return self.packed


def _make_window(docs):
    win = object.__new__(CausalBayesianNetworkWindow)
    win.doc_var = DummyVar()
    win.doc_cb = DummyCB()
    win.canvas = DummyCanvas()
    win.toolbox = DummyToolbox()
    win.app = types.SimpleNamespace(cbn_docs=docs, active_cbn=None)
    win.load_doc = lambda *a, **k: None
    return win


def test_toolbox_hidden_without_analysis():
    win = _make_window([])
    CausalBayesianNetworkWindow.refresh_docs(win)
    assert not win.toolbox.packed


def test_toolbox_shown_with_analysis():
    doc = types.SimpleNamespace(name="A")
    win = _make_window([doc])
    CausalBayesianNetworkWindow.refresh_docs(win)
    assert win.toolbox.packed
