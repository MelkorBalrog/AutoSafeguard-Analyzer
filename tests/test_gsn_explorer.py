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


def test_orphan_nodes_displayed_in_explorer():
    root = GSNNode("Root", "Goal")
    orphan = GSNNode("Loose", "Goal")
    diag = GSNDiagram(root)
    diag.add_node(orphan)

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
    explorer.app = types.SimpleNamespace(gsn_modules=[], gsn_diagrams=[diag])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)

    texts = [meta["text"] for meta in explorer.tree.items.values()]
    assert "Loose" in texts


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


def test_open_item_delegates_to_app(monkeypatch):
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)

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
    explorer.app = types.SimpleNamespace(gsn_modules=[], gsn_diagrams=[diag], opened=None)
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)

    for iid, (typ, obj) in explorer.item_map.items():
        if obj is diag:
            explorer.tree.selection_item = iid
            break

    explorer.app.open_gsn_diagram = lambda d: setattr(explorer.app, "opened", d)
    GSNExplorer.open_item(explorer)

    assert explorer.app.opened is diag


def test_rename_node(monkeypatch):
    root = GSNNode("Root", "Goal")
    child = GSNNode("Child", "Goal")
    root.add_child(child)
    diag = GSNDiagram(root)
    diag.add_node(child)

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
    explorer.app = types.SimpleNamespace(gsn_modules=[], gsn_diagrams=[diag])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)

    for iid, (typ, obj) in explorer.item_map.items():
        if obj is child:
            explorer.tree.selection_item = iid
            break

    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Renamed")

    GSNExplorer.rename_item(explorer)

    assert child.user_name == "Renamed"


def _setup_dummy_tree():
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

    return DummyTree()


def test_rename_module_disallowed(monkeypatch):
    mod = GSNModule("Pkg")
    explorer = GSNExplorer.__new__(GSNExplorer)
    explorer.tree = _setup_dummy_tree()
    explorer.app = types.SimpleNamespace(gsn_modules=[mod], gsn_diagrams=[])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None
    GSNExplorer.populate(explorer)
    for iid, (typ, obj) in explorer.item_map.items():
        if obj is mod:
            explorer.tree.selection_item = iid
            break
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "New")
    GSNExplorer.rename_item(explorer)
    assert mod.name == "Pkg"


def test_rename_module_node_disallowed(monkeypatch):
    root = GSNNode("Root", "Goal")
    mnode = GSNNode("Pkg", "Module")
    root.add_child(mnode)
    diag = GSNDiagram(root)
    diag.add_node(mnode)
    explorer = GSNExplorer.__new__(GSNExplorer)
    explorer.tree = _setup_dummy_tree()
    explorer.app = types.SimpleNamespace(gsn_modules=[], gsn_diagrams=[diag])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None
    GSNExplorer.populate(explorer)
    for iid, (typ, obj) in explorer.item_map.items():
        if obj is mnode:
            explorer.tree.selection_item = iid
            break
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "New")
    GSNExplorer.rename_item(explorer)
    assert mnode.user_name == "Pkg"


def test_delete_node():
    root = GSNNode("Root", "Goal")
    child = GSNNode("Child", "Goal")
    root.add_child(child)
    diag = GSNDiagram(root)
    diag.add_node(child)

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
    explorer.app = types.SimpleNamespace(gsn_modules=[], gsn_diagrams=[diag])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)

    for iid, (typ, obj) in explorer.item_map.items():
        if obj is child:
            explorer.tree.selection_item = iid
            break

    GSNExplorer.delete_item(explorer)

    assert child not in diag.nodes
    assert child not in root.children


def test_drag_diagram_into_module():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    mod = GSNModule("Pkg")

    explorer = GSNExplorer.__new__(GSNExplorer)

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0
            self.selection_item = None
            self.item_for_y = {}

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

        def identify_row(self, y):
            return self.item_for_y.get(y, "")

    explorer.tree = DummyTree()
    explorer.app = types.SimpleNamespace(gsn_modules=[mod], gsn_diagrams=[diag])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)

    for iid, (typ, obj) in explorer.item_map.items():
        if obj is diag:
            diag_id = iid
        elif obj is mod:
            mod_id = iid
    explorer.tree.item_for_y[0] = diag_id
    explorer.tree.item_for_y[1] = mod_id

    explorer._on_drag_start(types.SimpleNamespace(y=0))
    explorer._on_drag_end(types.SimpleNamespace(y=1))

    assert diag in mod.diagrams
    assert diag not in explorer.app.gsn_diagrams


def test_drag_diagram_to_root():
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
            self.item_for_y = {}

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

        def identify_row(self, y):
            return self.item_for_y.get(y, "")

    explorer.tree = DummyTree()
    explorer.app = types.SimpleNamespace(gsn_modules=[mod], gsn_diagrams=[])
    explorer.item_map = {}
    explorer.module_icon = None
    explorer.diagram_icon = None
    explorer.node_icons = {}
    explorer.default_node_icon = None

    GSNExplorer.populate(explorer)

    for iid, (typ, obj) in explorer.item_map.items():
        if obj is diag:
            diag_id = iid
    explorer.tree.item_for_y[0] = diag_id

    explorer._on_drag_start(types.SimpleNamespace(y=0))
    explorer._on_drag_end(types.SimpleNamespace(y=42))

    assert diag not in mod.diagrams
    assert diag in explorer.app.gsn_diagrams
