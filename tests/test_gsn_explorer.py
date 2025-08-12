import types

from tkinter import simpledialog

from gsn import GSNNode, GSNDiagram, GSNModule
from gui.gsn_explorer import GSNExplorer


def test_gsn_explorer_populates_modules_and_diagrams():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    mod = GSNModule("Pkg")
    mod.diagrams.append(diag)

    explorer = GSNExplorer.__new__(GSNExplorer)

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

        def parent(self, item):
            return self.items[item]["parent"]

        def selection(self):
            return (self.selection_item,) if self.selection_item else ()

    explorer.tree = DummyTree()
    explorer.app = types.SimpleNamespace(gsn_modules=[mod], gsn_diagrams=[])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)

    texts = [meta["text"] for meta in explorer.tree.items.values()]
    assert "Pkg" in texts
    assert "Root" in texts


def test_new_diagram_only_in_module(monkeypatch):
    mod = GSNModule("Pkg")
    explorer = GSNExplorer.__new__(GSNExplorer)

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

        def parent(self, item):
            return self.items[item]["parent"]

        def selection(self):
            return (self.selection_item,) if self.selection_item else ()

    explorer.tree = DummyTree()
    explorer.app = types.SimpleNamespace(gsn_modules=[mod], gsn_diagrams=[])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)
    # select the module
    for iid, (typ, obj) in explorer.item_map.items():
        if obj is mod:
            explorer.tree.selection_item = iid
            break

    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Goal1")

    GSNExplorer.new_diagram(explorer)

    assert len(mod.diagrams) == 1
    assert explorer.app.gsn_diagrams == []
