import types
from tkinter import simpledialog

from gsn import GSNNode, GSNDiagram, GSNModule
from analysis.safety_case import SafetyCaseLibrary
from gui.safety_case_explorer import SafetyCaseExplorer
from gui.safety_case_table import SafetyCaseTable
from gui import messagebox


class DummyTree:
    def __init__(self):
        self.items = {}
        self.counter = 0
        self.selection_item = None

    def delete(self, *items):
        self.items = {}

    def get_children(self, item=""):
        return [iid for iid, meta in self.items.items() if meta["parent"] == item]

    def insert(self, parent, index, text="", image=None):
        iid = f"i{self.counter}"
        self.counter += 1
        self.items[iid] = {"parent": parent, "text": text}
        return iid

    def selection(self):
        return (self.selection_item,) if self.selection_item else ()


class DummyTable:
    def __init__(self):
        self.items = []

    def delete(self, *items):
        self.items = []

    def get_children(self, item=""):
        return list(range(len(self.items)))

    def insert(self, parent, index, values=(), tags=()):
        self.items.append(values)
        return str(len(self.items) - 1)


def test_create_edit_delete_case(monkeypatch):
    root = GSNNode("G", "Goal")
    sol = GSNNode("S", "Solution")
    root.add_child(sol)
    diag = GSNDiagram(root)
    diag.add_node(sol)

    explorer = SafetyCaseExplorer.__new__(SafetyCaseExplorer)
    explorer.tree = DummyTree()
    explorer.app = types.SimpleNamespace(gsn_diagrams=[diag])
    explorer.library = SafetyCaseLibrary()
    explorer.item_map = {}
    explorer.case_icon = explorer.solution_icon = None

    SafetyCaseExplorer.populate(explorer)

    inputs = iter(["Case1", root.user_name])
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: next(inputs))
    SafetyCaseExplorer.new_case(explorer)
    assert len(explorer.library.cases) == 1
    texts = [meta["text"] for meta in explorer.tree.items.values()]
    assert "Case1" in texts
    assert "S" in texts

    for iid, (typ, obj) in explorer.item_map.items():
        if typ == "case":
            explorer.tree.selection_item = iid
            break
    inputs = iter(["Renamed", root.user_name])
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: next(inputs))
    SafetyCaseExplorer.edit_case(explorer)
    assert explorer.library.cases[0].name == "Renamed"
    for iid, (typ, obj) in explorer.item_map.items():
        if typ == "case":
            explorer.tree.selection_item = iid
            break
    monkeypatch.setattr(messagebox, "askokcancel", lambda *a, **k: True)
    SafetyCaseExplorer.delete_case(explorer)
    assert explorer.library.cases == []


def test_create_case_from_module(monkeypatch):
    root = GSNNode("G", "Goal")
    diag = GSNDiagram(root)
    module = GSNModule("M")
    module.diagrams.append(diag)

    explorer = SafetyCaseExplorer.__new__(SafetyCaseExplorer)
    explorer.tree = DummyTree()
    explorer.app = types.SimpleNamespace(gsn_diagrams=[], gsn_modules=[module])
    explorer.library = SafetyCaseLibrary()
    explorer.item_map = {}
    explorer.case_icon = explorer.solution_icon = None

    SafetyCaseExplorer.populate(explorer)

    inputs = iter(["Case2", root.user_name])
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: next(inputs))
    SafetyCaseExplorer.new_case(explorer)
    assert explorer.library.cases and explorer.library.cases[0].diagram is diag


def test_safety_case_table_lists_solutions():
    root = GSNNode("G", "Goal")
    sol1 = GSNNode("S1", "Solution", description="d1")
    root.add_child(sol1)
    diag = GSNDiagram(root)
    diag.add_node(sol1)
    lib = SafetyCaseLibrary()
    case = lib.create_case("Case", diag)

    table = SafetyCaseTable.__new__(SafetyCaseTable)
    table.case = case
    table.tree = DummyTable()
    SafetyCaseTable.populate(table)
    assert table.tree.items and table.tree.items[0][0] == "S1"
