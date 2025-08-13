import os
import sys
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Stub out Pillow modules so AutoML can be imported without the dependency
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))

from gsn import GSNNode, GSNDiagram
from AutoML import FaultTreeApp
from analysis.constants import CHECK_MARK


class DummyTree:
    def __init__(self, master=None, *, columns=None, show=None, selectmode=None):
        self.columns = list(columns or [])
        self.data = {}
        self.counter = 0
        self.bindings = {}
        self.next_column = "Evidence OK"

    def heading(self, column, text=""):
        pass

    def column(self, column, width=None, anchor=None):
        pass

    def pack(self, **kwargs):
        pass

    def insert(self, parent, index, values=None, tags=()):
        iid = f"i{self.counter}"
        self.counter += 1
        self.data[iid] = {"values": list(values or []), "tags": tags}
        return iid

    def get_children(self, item=""):
        return list(self.data.keys())

    def delete(self, iid):
        self.data.pop(iid, None)

    def bind(self, event, callback):
        self.bindings[event] = callback

    def identify_row(self, y):
        return next(iter(self.data.keys()), "")

    def identify_column(self, x):
        idx = self.columns.index(self.next_column) + 1
        return f"#{idx}"

    def item(self, iid, option):
        if option == "tags":
            return self.data.get(iid, {}).get("tags", ())
        return None

    def set(self, iid, column, value=None):
        idx = self.columns.index(column)
        if value is None:
            return self.data[iid]["values"][idx]
        self.data[iid]["values"][idx] = value

    def winfo_exists(self):
        return True


class DummyTab:
    def winfo_exists(self):
        return True

    def winfo_children(self):
        return []

def test_safety_case_lists_and_toggles(monkeypatch):
    root = GSNNode("G", "Goal")
    sol = GSNNode("E", "Solution")
    root.add_child(sol)
    diag = GSNDiagram(root)
    diag.add_node(sol)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.doc_nb = types.SimpleNamespace(select=lambda tab: None)
    app._new_tab = lambda title: DummyTab()
    app.all_gsn_diagrams = [diag]

    monkeypatch.setattr("AutoML.ttk.Treeview", DummyTree)
    monkeypatch.setattr("AutoML.messagebox.askokcancel", lambda *a, **k: True)

    FaultTreeApp.show_safety_case(app)
    tree = app._safety_case_tree
    assert len(tree.data) == 1
    iid = next(iter(tree.data))
    assert tree.data[iid]["values"][0] == "E"

    event = types.SimpleNamespace(x=0, y=0)
    tree.bindings["<Double-1>"](event)
    assert sol.evidence_sufficient
    assert tree.data[iid]["values"][5] == CHECK_MARK

    app.refresh_safety_case_table()
    iid = next(iter(tree.data))
    assert tree.data[iid]["values"][5] == CHECK_MARK


def test_safety_case_cancel_does_not_toggle(monkeypatch):
    root = GSNNode("G", "Goal")
    sol = GSNNode("E", "Solution")
    root.add_child(sol)
    diag = GSNDiagram(root)
    diag.add_node(sol)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.doc_nb = types.SimpleNamespace(select=lambda tab: None)
    app._new_tab = lambda title: types.SimpleNamespace(
        winfo_exists=lambda: True, winfo_children=lambda: []
    )
    app.all_gsn_diagrams = [diag]

    monkeypatch.setattr("AutoML.ttk.Treeview", DummyTree)
    monkeypatch.setattr("AutoML.messagebox.askokcancel", lambda *a, **k: False)

    FaultTreeApp.show_safety_case(app)
    tree = app._safety_case_tree
    iid = next(iter(tree.data))

    called = {"count": 0}

    def fake_refresh():
        called["count"] += 1

    app.refresh_safety_case_table = fake_refresh

    class Notebook:
        def select(self):
            return "tab1"

        def nametowidget(self, tab_id):
            assert tab_id == "tab1"
            return app._safety_case_tab

    event = types.SimpleNamespace(widget=Notebook())
    app._on_tab_change(event)

    assert called["count"] == 1


def test_safety_case_add_notes(monkeypatch):
    root = GSNNode("G", "Goal")
    sol = GSNNode("E", "Solution")
    root.add_child(sol)
    diag = GSNDiagram(root)
    diag.add_node(sol)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.doc_nb = types.SimpleNamespace(select=lambda tab: None)
    app._new_tab = lambda title: DummyTab()
    app.all_gsn_diagrams = [diag]

    monkeypatch.setattr("AutoML.ttk.Treeview", DummyTree)
    monkeypatch.setattr("AutoML.simpledialog.askstring", lambda title, prompt, initialvalue=None: "note")

    FaultTreeApp.show_safety_case(app)
    tree = app._safety_case_tree
    tree.next_column = "Notes"
    event = types.SimpleNamespace(x=0, y=0)
    tree.bindings["<Double-1>"](event)
    iid = next(iter(tree.data))
    assert sol.manager_notes == "note"
    assert tree.data[iid]["values"][6] == "note"