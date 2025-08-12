import types

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

        def delete(self, *items):
            self.items = {}

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def insert(self, parent, index, text=""):
            iid = f"i{self.counter}"
            self.counter += 1
            self.items[iid] = {"parent": parent, "text": text}
            return iid

        def parent(self, item):
            return self.items[item]["parent"]

        def selection(self):
            return ()

    explorer.tree = DummyTree()
    explorer.app = types.SimpleNamespace(gsn_modules=[mod], gsn_diagrams=[])
    explorer.item_map = {}

    GSNExplorer.populate(explorer)

    texts = [meta["text"] for meta in explorer.tree.items.values()]
    assert "Pkg" in texts
    assert "Root" in texts
