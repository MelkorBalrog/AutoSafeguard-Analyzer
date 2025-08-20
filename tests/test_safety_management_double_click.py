import types

from gui.safety_management_explorer import SafetyManagementExplorer
from analysis.safety_management import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository


def test_double_click_opens_diagram_with_phase(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag_id = toolbox.create_diagram("Gov (Phase1)")

    explorer = SafetyManagementExplorer.__new__(SafetyManagementExplorer)

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0
            self.selection_item = None

        def delete(self, *items):
            self.items = {}

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def insert(self, parent, index, text="", image=None, **_kwargs):
            iid = f"i{self.counter}"
            self.counter += 1
            self.items[iid] = {"parent": parent, "text": text}
            return iid

        def parent(self, item):
            return self.items[item]["parent"]

        def selection(self):
            return (self.selection_item,) if self.selection_item else ()

    explorer.tree = DummyTree()
    explorer.toolbox = toolbox
    explorer.item_map = {}
    explorer.folder_icon = None
    explorer.diagram_icon = None
    calls = []
    explorer.app = types.SimpleNamespace(open_arch_window=lambda _id: calls.append(_id))

    SafetyManagementExplorer.populate(explorer)

    # locate diagram iid
    for iid, (typ, obj) in explorer.item_map.items():
        if typ == "diagram" and obj == "Gov (Phase1)":
            explorer.tree.selection_item = iid
            break

    explorer.open_item()
    assert calls == [diag_id]
