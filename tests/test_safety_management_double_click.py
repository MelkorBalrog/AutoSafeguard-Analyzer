import types

from gui.safety_management_explorer import SafetyManagementExplorer
from analysis.safety_management import SafetyManagementToolbox
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from AutoML import AutoMLApp


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
    explorer.app = types.SimpleNamespace(
        window_controllers=types.SimpleNamespace(open_arch_window=lambda _id: calls.append(_id))
    )

    SafetyManagementExplorer.populate(explorer)

    # locate diagram iid
    for iid, (typ, obj) in explorer.item_map.items():
        if typ == "diagram" and obj == "Gov (Phase1)":
            explorer.tree.selection_item = iid
            break

    explorer.open_item()
    assert calls == [diag_id]


def test_analysis_tree_double_click_opens_diagram(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Governance Diagram", name="Gov")
    app = AutoMLApp.__new__(AutoMLApp)

    class DummyTree:
        def __init__(self):
            self.items = {
                "root": {"text": "Safety & Security Governance Diagrams", "tags": (), "parent": ""},
                "d1": {"text": "Gov", "tags": ("gov", "0"), "parent": "root"},
            }
            self._focus = "root"

        def focus(self, item=None):
            if item is None:
                return self._focus
            self._focus = item

        def identify_row(self, _y):
            return "d1"

        def item(self, iid, opt):
            return self.items[iid][opt]

        def parent(self, iid):
            return self.items[iid]["parent"]

    app.analysis_tree = DummyTree()
    called = {"open": None, "explorer": False}
    app.open_management_window = lambda idx: called.__setitem__("open", idx)
    app.manage_safety_management = lambda: called.__setitem__("explorer", True)

    app.on_analysis_tree_double_click(types.SimpleNamespace(y=10))

    assert called["open"] == 0
    assert not called["explorer"]


def test_analysis_tree_double_click_handles_extra_tags(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Governance Diagram", name="Gov")
    app = AutoMLApp.__new__(AutoMLApp)

    class DummyTree:
        def __init__(self):
            self.items = {
                "root": {
                    "text": "Safety & Security Governance Diagrams",
                    "tags": (),
                    "parent": "",
                },
                "d1": {
                    "text": "Gov",
                    "tags": ("gov", "0", "extra"),
                    "parent": "root",
                },
            }
            self._focus = "root"

        def focus(self, item=None):
            if item is None:
                return self._focus
            self._focus = item

        def identify_row(self, _y):
            return "d1"

        def item(self, iid, opt):
            return self.items[iid][opt]

        def parent(self, iid):
            return self.items[iid]["parent"]

    app.analysis_tree = DummyTree()
    called = {"open": None, "explorer": False}
    app.open_management_window = lambda idx: called.__setitem__("open", idx)
    app.manage_safety_management = lambda: called.__setitem__("explorer", True)

    app.on_analysis_tree_double_click(types.SimpleNamespace(y=5))

    assert called["open"] == 0
    assert not called["explorer"]
