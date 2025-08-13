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
        self.selection_value = ()

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

    def selection(self):
        return self.selection_value

    def selection_set(self, row):
        self.selection_value = (row,)


class DummyTab:
    def winfo_exists(self):
        return True

    def winfo_children(self):
        return []


class DummyButton:
    def __init__(self, *a, **k):
        pass

    def pack(self, *a, **k):
        pass


class DummyMenu:
    def __init__(self, *a, **k):
        pass

    def add_command(self, *a, **k):
        pass

    def post(self, *a, **k):
        pass

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
    app.push_undo_state = lambda: None

    monkeypatch.setattr("AutoML.ttk.Treeview", DummyTree)
    monkeypatch.setattr("AutoML.ttk.Button", DummyButton)
    monkeypatch.setattr("AutoML.tk.Menu", DummyMenu)
    monkeypatch.setattr("AutoML.messagebox.askokcancel", lambda *a, **k: True)

    FaultTreeApp.show_safety_case(app)
    tree = app._safety_case_tree
    assert len(tree.data) == 1
    iid = next(iter(tree.data))
    assert tree.data[iid]["values"][0] == "E"

    event = types.SimpleNamespace(x=0, y=0)
    tree.bindings["<Double-Button-1>"](event)
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
    app.push_undo_state = lambda: None

    monkeypatch.setattr("AutoML.ttk.Treeview", DummyTree)
    monkeypatch.setattr("AutoML.ttk.Button", DummyButton)
    monkeypatch.setattr("AutoML.tk.Menu", DummyMenu)
    monkeypatch.setattr("AutoML.messagebox.askokcancel", lambda *a, **k: False)


def test_safety_case_edit_updates_table(monkeypatch):
    root = GSNNode("G", "Goal")
    sol = GSNNode("E", "Solution")
    root.add_child(sol)
    diag = GSNDiagram(root)
    diag.add_node(sol)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.doc_nb = types.SimpleNamespace(select=lambda tab: None)
    app._new_tab = lambda title: DummyTab()
    app.all_gsn_diagrams = [diag]
    app.push_undo_state = lambda: None

    monkeypatch.setattr("AutoML.ttk.Treeview", DummyTree)
    monkeypatch.setattr("AutoML.ttk.Button", DummyButton)
    monkeypatch.setattr("AutoML.tk.Menu", DummyMenu)

    called = {}

    def fake_config(master, node, diag):
        called["ok"] = True
        node.work_product = "WP"

    monkeypatch.setattr("AutoML.GSNElementConfig", fake_config)

    FaultTreeApp.show_safety_case(app)
    tree = app._safety_case_tree
    iid = next(iter(tree.data))
    tree.selection_set(iid)
    app._edit_safety_case_item()
    assert called.get("ok")
    iid = next(iter(tree.data))
    assert tree.data[iid]["values"][2] == "WP"


def test_safety_case_undo_redo_toggle(monkeypatch):
    root = GSNNode("G", "Goal")
    sol = GSNNode("E", "Solution")
    root.add_child(sol)
    diag = GSNDiagram(root)
    diag.add_node(sol)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.doc_nb = types.SimpleNamespace(select=lambda tab: None)
    app._new_tab = lambda title: DummyTab()
    app.all_gsn_diagrams = [diag]
    app.gsn_diagrams = [diag]
    app.update_views = lambda: None
    app._undo_stack = []
    app._redo_stack = []

    def export_model_data(include_versions=False):
        return {
            "gsn_diagrams": [d.to_dict() for d in app.gsn_diagrams],
            "gsn_modules": [],
        }

    def apply_model_data(data):
        app.gsn_diagrams = [GSNDiagram.from_dict(d) for d in data.get("gsn_diagrams", [])]
        app.all_gsn_diagrams = list(app.gsn_diagrams)

    app.export_model_data = export_model_data
    app.apply_model_data = apply_model_data
    app.push_undo_state = FaultTreeApp.push_undo_state.__get__(app)
    app.undo = FaultTreeApp.undo.__get__(app)
    app.redo = FaultTreeApp.redo.__get__(app)

    monkeypatch.setattr("AutoML.ttk.Treeview", DummyTree)
    monkeypatch.setattr("AutoML.ttk.Button", DummyButton)
    monkeypatch.setattr("AutoML.tk.Menu", DummyMenu)
    monkeypatch.setattr("AutoML.messagebox.askokcancel", lambda *a, **k: True)

    FaultTreeApp.show_safety_case(app)
    tree = app._safety_case_tree
    event = types.SimpleNamespace(x=0, y=0)
    tree.bindings["<Double-Button-1>"](event)
    assert app.gsn_diagrams[0].nodes[1].evidence_sufficient

    app.undo()
    assert not app.gsn_diagrams[0].nodes[1].evidence_sufficient

    app.redo()
    assert app.gsn_diagrams[0].nodes[1].evidence_sufficient
