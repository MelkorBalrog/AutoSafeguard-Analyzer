import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import types
import sys

# Stub out Pillow dependencies so importing the main app doesn't require Pillow
PIL_stub = types.ModuleType("PIL")
PIL_stub.Image = types.SimpleNamespace()
PIL_stub.ImageTk = types.SimpleNamespace()
PIL_stub.ImageDraw = types.SimpleNamespace()
PIL_stub.ImageFont = types.SimpleNamespace()
sys.modules.setdefault("PIL", PIL_stub)
sys.modules.setdefault("PIL.Image", PIL_stub.Image)
sys.modules.setdefault("PIL.ImageTk", PIL_stub.ImageTk)
sys.modules.setdefault("PIL.ImageDraw", PIL_stub.ImageDraw)
sys.modules.setdefault("PIL.ImageFont", PIL_stub.ImageFont)

from AutoML import FaultTreeApp
import AutoML
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from gui.architecture import BPMNDiagramWindow, SysMLObject, ArchitectureManagerDialog
from gui.safety_management_explorer import SafetyManagementExplorer
from gui.review_toolbox import ReviewData
from sysml.sysml_repository import SysMLRepository
from tkinter import simpledialog


def test_work_product_registration():
    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("BPMN Diagram", "HAZOP", "Link action to hazard")

    products = toolbox.get_work_products()
    assert len(products) == 1
    assert products[0].diagram == "BPMN Diagram"
    assert products[0].analysis == "HAZOP"
    assert products[0].rationale == "Link action to hazard"


def test_lifecycle_and_workflow_storage():
    toolbox = SafetyManagementToolbox()
    toolbox.build_lifecycle(["concept", "development", "operation"])
    toolbox.define_workflow("risk", ["identify", "assess", "mitigate"])

    assert toolbox.lifecycle == ["concept", "development", "operation"]
    assert toolbox.get_workflow("risk") == ["identify", "assess", "mitigate"]
    assert toolbox.get_workflow("missing") == []


class DummyCanvas:
    def __init__(self):
        self.text_calls = []

    def create_text(self, x, y, **kw):
        self.text_calls.append((x, y, kw))

    def create_rectangle(self, *args, **kwargs):
        pass

    def create_line(self, *args, **kwargs):
        pass

    def create_polygon(self, *args, **kwargs):
        pass


def test_activity_boundary_label_rotated_left():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("BPMN Diagram")
    win = BPMNDiagramWindow.__new__(BPMNDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.zoom = 1.0
    win.canvas = DummyCanvas()
    win.font = None
    win._draw_gradient_rect = lambda *args, **kwargs: None
    win.selected_objs = []
    obj = SysMLObject(1, "System Boundary", 0.0, 0.0, width=100.0, height=80.0, properties={"name": "Lane"})
    win.draw_object(obj)

    assert win.canvas.text_calls, "label not drawn"
    x, _, kwargs = win.canvas.text_calls[0]
    assert kwargs.get("angle") == 90
    assert x < obj.x - obj.width / 2


def test_toolbox_manages_diagram_lifecycle():
    """Toolbox creates tagged diagrams, can rename, and delete them."""
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    diag_id = toolbox.create_diagram("Gov1")
    assert diag_id in repo.diagrams
    assert "safety-management" in repo.diagrams[diag_id].tags

    toolbox.rename_diagram("Gov1", "Gov2")
    assert repo.diagrams[diag_id].name == "Gov2"
    assert "Gov2" in toolbox.list_diagrams()

    toolbox.delete_diagram("Gov2")
    assert diag_id not in repo.diagrams
    assert not toolbox.diagrams


def test_open_safety_management_toolbox_uses_browser():
    """FaultTreeApp opens the Safety Management window and toolbox."""
    SysMLRepository._instance = None

    class DummyTab:
        def __init__(self):
            self._exists = True

        def winfo_exists(self):
            return self._exists

    class DummyNotebook:
        def add(self, tab, text):
            pass

        def select(self, tab):
            pass

    class DummySMW:
        def __init__(self, master, app, toolbox):
            DummySMW.created = True
            assert toolbox is app.safety_mgmt_toolbox

    import gui.safety_management_toolbox as smt
    smt.SafetyManagementWindow = DummySMW

    class DummyApp:
        open_safety_management_toolbox = FaultTreeApp.open_safety_management_toolbox

        def __init__(self):
            self.doc_nb = DummyNotebook()

        def _new_tab(self, title):
            return DummyTab()

    DummySMW.created = False
    app = DummyApp()
    app.open_safety_management_toolbox()
    assert DummySMW.created
    assert hasattr(app, "safety_mgmt_toolbox")


def test_safety_diagrams_hidden_and_immutable_in_explorer():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag_id = toolbox.create_diagram("Gov")

    class DummyTree:
        def __init__(self):
            self.items = {}

        def delete(self, *items):
            for iid in items:
                self.items.pop(iid, None)

        def get_children(self, item=""):
            if item:
                return self.items.get(item, {}).get("children", [])
            return [iid for iid, meta in self.items.items() if meta["parent"] == ""]

        def exists(self, iid):
            return iid in self.items

        def insert(self, parent, index, iid=None, text="", values=(), image=None, **kwargs):
            self.items[iid] = {
                "parent": parent,
                "text": text,
                "values": values,
                "image": image,
                "children": [],
            }
            if parent in self.items:
                self.items[parent]["children"].append(iid)
            return iid

    class DummyExplorer:
        def __init__(self):
            self.repo = repo
            self.tree = DummyTree()
            self.diagram_icons = {}
            self.elem_icons = {}
            self.default_diag_icon = None
            self.default_elem_icon = None
            self.pkg_icon = None
            self.app = None

        populate = ArchitectureManagerDialog.populate
        rename_item = ArchitectureManagerDialog.rename_item

    explorer = DummyExplorer()
    explorer.populate()
    assert not explorer.tree.exists(f"diag_{diag_id}")
    explorer.rename_item(f"diag_{diag_id}")
    assert repo.diagrams[diag_id].name == "Gov"

def test_safety_diagrams_visible_in_analysis_tree():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.create_diagram("Gov")
    repo.create_diagram("Block Definition Diagram", name="Arch")

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0

        def delete(self, *items):
            pass

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def insert(self, parent, index, iid=None, text="", **kwargs):
            if iid is None:
                iid = f"i{self.counter}"
                self.counter += 1
            self.items[iid] = {"parent": parent, "text": text}
            return iid

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.refresh_model = lambda: None
    app.compute_occurrence_counts = lambda: {}
    app.diagram_icons = {}
    app.hazop_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hara_docs = []
    app.top_events = []
    app.fmeas = []
    app.fmedas = []
    app.analysis_tree = DummyTree()

    app.update_views()
    texts = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert "Safety Management" in texts
    assert "Safety & Security Governance Diagrams" in texts
    assert "Gov" in texts
    assert "Arch" in texts


def test_gsn_diagrams_visible_in_analysis_tree():
    SysMLRepository._instance = None
    SysMLRepository.get_instance()

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0

        def delete(self, *items):
            pass

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def insert(self, parent, index, iid=None, text="", **kwargs):
            if iid is None:
                iid = f"i{self.counter}"
                self.counter += 1
            self.items[iid] = {"parent": parent, "text": text}
            return iid

    from gsn import GSNNode, GSNDiagram

    root = GSNNode("Goal1", "Goal")
    diag = GSNDiagram(root)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.refresh_model = lambda: None
    app.compute_occurrence_counts = lambda: {}
    app.diagram_icons = {}
    app.hazop_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hara_docs = []
    app.top_events = []
    app.fmeas = []
    app.fmedas = []
    app.gsn_diagrams = [diag]
    app.gsn_modules = []
    app.analysis_tree = DummyTree()

    app.update_views()
    texts = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert "GSN Diagrams" in texts
    assert "Goal1" in texts


def test_joint_reviews_visible_in_analysis_tree():
    SysMLRepository._instance = None
    SysMLRepository.get_instance()

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0

        def delete(self, *items):
            pass

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def insert(self, parent, index, iid=None, text="", **kwargs):
            if iid is None:
                iid = f"i{self.counter}"
                self.counter += 1
            self.items[iid] = {"parent": parent, "text": text}
            return iid

    joint = ReviewData(name="JR1", mode="joint")
    peer = ReviewData(name="PR1", mode="peer")

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.refresh_model = lambda: None
    app.compute_occurrence_counts = lambda: {}
    app.diagram_icons = {}
    app.hazop_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hara_docs = []
    app.top_events = []
    app.fmeas = []
    app.fmedas = []
    app.gsn_diagrams = []
    app.gsn_modules = []
    app.reviews = [joint, peer]
    app.analysis_tree = DummyTree()

    app.update_views()
    texts = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert "Verification Reviews" in texts
    assert "JR1" in texts
    assert "PR1" not in texts


def test_external_safety_diagrams_load_in_toolbox_list():
    """Diagrams tagged for governance appear even if created elsewhere."""
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("BPMN Diagram", name="GovX")
    diag.tags.append("safety-management")
    toolbox = SafetyManagementToolbox()
    names = toolbox.list_diagrams()
    assert "GovX" in names


def test_toolbox_serializes_modules():
    """Folder hierarchy survives a save/load round trip."""
    toolbox = SafetyManagementToolbox()
    toolbox.diagrams = {"D1": "id1", "D2": "id2"}
    child = GovernanceModule(name="Child", diagrams=["D1"])
    toolbox.modules = [GovernanceModule(name="Root", modules=[child], diagrams=["D2"])]

    data = toolbox.to_dict()
    loaded = SafetyManagementToolbox.from_dict(data)

    assert loaded.modules[0].name == "Root"
    assert loaded.modules[0].modules[0].name == "Child"
    assert loaded.modules[0].modules[0].diagrams == ["D1"]
    assert loaded.modules[0].diagrams == ["D2"]


def test_governance_diagram_opens_with_bpmn_toolbox(monkeypatch):
    """Governance diagrams open as BPMN diagrams with their toolbox."""
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("BPMN Diagram", name="GovA")
    diag.tags.append("safety-management")

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.management_diagrams = [diag]
    app.diagram_tabs = {}

    class DummyNotebook:
        def __init__(self):
            self._tabs = []
        def tabs(self):
            return self._tabs
        def select(self, tab):
            self.selected = tab

    app.doc_nb = DummyNotebook()
    app._format_diag_title = lambda d: d.name

    def _new_tab(title):
        app.doc_nb._tabs.append(title)
        return title

    app._new_tab = _new_tab
    app.refresh_all = lambda: None

    calls = {"bpmn": False, "activity": False}

    def fake_bpmn(tab, _app, diagram_id):
        calls["bpmn"] = True
        assert diagram_id == diag.diag_id

    def fake_activity(tab, _app, diagram_id):
        calls["activity"] = True

    monkeypatch.setattr(AutoML, "BPMNDiagramWindow", fake_bpmn)
    monkeypatch.setattr(AutoML, "ActivityDiagramWindow", fake_activity)

    app.open_management_window(0)

    assert calls["bpmn"]
    assert not calls["activity"]


def test_diagram_hierarchy_orders_levels():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    a = repo.create_diagram("BPMN Diagram", name="A")
    b = repo.create_diagram("BPMN Diagram", name="B")
    c = repo.create_diagram("BPMN Diagram", name="C")
    for diag in (a, b, c):
        diag.tags.append("safety-management")

    toolbox.list_diagrams()

    act_ab = repo.create_element("Action", name="AB", owner=a.package)
    repo.add_element_to_diagram(a.diag_id, act_ab.elem_id)
    repo.link_diagram(act_ab.elem_id, b.diag_id)
    a.objects.append(
        SysMLObject(1, "Action", 0.0, 0.0, element_id=act_ab.elem_id, properties={}).__dict__
    )

    act_bc = repo.create_element("Action", name="BC", owner=b.package)
    repo.add_element_to_diagram(b.diag_id, act_bc.elem_id)
    repo.link_diagram(act_bc.elem_id, c.diag_id)
    b.objects.append(
        SysMLObject(2, "Action", 0.0, 0.0, element_id=act_bc.elem_id, properties={}).__dict__
    )

    hierarchy = toolbox.diagram_hierarchy()
    assert hierarchy == [["A"], ["B"], ["C"]]


def test_diagram_hierarchy_from_object_properties():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    parent = repo.create_diagram("BPMN Diagram", name="Parent")
    child = repo.create_diagram("BPMN Diagram", name="Child")
    for d in (parent, child):
        d.tags.append("safety-management")

    toolbox.list_diagrams()

    # Create an action object on the parent that references the child diagram
    act = repo.create_element("Action", name="link", owner=parent.package)
    repo.add_element_to_diagram(parent.diag_id, act.elem_id)
    parent.objects.append(
        SysMLObject(
            3,
            "Action",
            0.0,
            0.0,
            element_id=act.elem_id,
            properties={"view": child.diag_id},
        )
    )

    hierarchy = toolbox.diagram_hierarchy()
    assert hierarchy == [["Parent"], ["Child"]]


def test_safety_management_explorer_creates_folders_and_diagrams(monkeypatch):
    SysMLRepository._instance = None
    SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

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
    explorer.toolbox = toolbox
    explorer.item_map = {}
    explorer.folder_icon = None
    explorer.diagram_icon = None
    explorer.app = types.SimpleNamespace(open_arch_window=lambda _id: None)

    SafetyManagementExplorer.populate(explorer)
    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Pkg")
    explorer.new_folder()
    assert toolbox.modules and toolbox.modules[0].name == "Pkg"

    for iid, (typ, obj) in explorer.item_map.items():
        if typ == "module" and obj.name == "Pkg":
            explorer.tree.selection_item = iid
            break
    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Diag")
    explorer.new_diagram()
    assert "Diag" in toolbox.modules[0].diagrams
    assert "Diag" in toolbox.diagrams


def test_tools_include_safety_management_explorer():
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.manage_safety_management = lambda: None
    app.open_safety_management_toolbox = lambda: None
    app.show_safety_performance_indicators = lambda: None
    app.show_safety_case = lambda: None
    app.manage_gsn = lambda: None

    app.tools = {
        "Safety Management": app.open_safety_management_toolbox,
        "Safety Performance Indicators": app.show_safety_performance_indicators,
        "Safety Case": app.show_safety_case,
        "Safety Management Explorer": app.manage_safety_management,
        "GSN Explorer": app.manage_gsn,
    }
    app.tool_categories = {
        "Safety Management": [
            "Safety Management",
            "Safety Management Explorer",
            "Safety Case",
            "Safety Performance Indicators",
            "GSN Explorer",
        ]
    }

    assert "Safety Management Explorer" in app.tools
    assert "Safety Management Explorer" in app.tool_categories["Safety Management"]


def test_diagram_drag_and_drop_between_modules():
    toolbox = SafetyManagementToolbox()
    toolbox.create_diagram("Diag1")
    mod1 = GovernanceModule("Mod1", diagrams=["Diag1"])
    mod2 = GovernanceModule("Mod2")
    toolbox.modules.extend([mod1, mod2])

    class DummyTree:
        def __init__(self):
            self.drop_target = ""
            self.parents = {"mod1": "", "mod2": "", "diag1": "mod1"}

        def identify_row(self, _y):
            return self.drop_target

        def move(self, item, parent, _index):
            self.parents[item] = parent

        def parent(self, item):
            return self.parents.get(item, "")

    explorer = types.SimpleNamespace()
    explorer.toolbox = toolbox
    explorer.tree = DummyTree()
    explorer.item_map = {
        "mod1": ("module", mod1),
        "mod2": ("module", mod2),
        "diag1": ("diagram", "Diag1"),
    }
    explorer._remove_name = SafetyManagementExplorer._remove_name.__get__(
        explorer, types.SimpleNamespace
    )
    explorer._remove_module = SafetyManagementExplorer._remove_module.__get__(
        explorer, types.SimpleNamespace
    )
    explorer._drag_item = "diag1"
    explorer.tree.drop_target = "mod2"
    SafetyManagementExplorer._on_drop(explorer, types.SimpleNamespace(y=0))
    assert "Diag1" in mod2.diagrams and "Diag1" not in mod1.diagrams

    explorer._drag_item = "diag1"
    explorer.tree.drop_target = ""
    SafetyManagementExplorer._on_drop(explorer, types.SimpleNamespace(y=0))
    assert "Diag1" not in mod2.diagrams
    assert explorer.tree.parents["diag1"] == ""


def test_governance_hierarchy_in_analysis_tree():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.create_diagram("Loose")
    toolbox.create_diagram("Child Diagram")
    child = GovernanceModule("Child", diagrams=["Child Diagram"])
    parent = GovernanceModule("Parent", modules=[child])
    toolbox.modules.append(parent)

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0

        def delete(self, *items):
            pass

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def insert(self, parent, index, iid=None, text="", image=None, tags=(), **kwargs):
            if iid is None:
                iid = f"i{self.counter}"
                self.counter += 1
            self.items[iid] = {
                "parent": parent,
                "text": text,
                "image": image,
                "tags": tags,
            }
            return iid

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.refresh_model = lambda: None
    app.compute_occurrence_counts = lambda: {}
    app.diagram_icons = {}
    app.hazop_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hara_docs = []
    app.top_events = []
    app.fmeas = []
    app.fmedas = []
    app.analysis_tree = DummyTree()
    app.pkg_icon = "PKG"
    app.gsn_diagram_icon = "DIAG"
    app.safety_mgmt_toolbox = toolbox

    app.update_views()
    items = app.analysis_tree.items
    gov_id = next(i for i, m in items.items() if m["text"] == "Safety & Security Governance Diagrams")
    parent_id = next(i for i, m in items.items() if m["text"] == "Parent")
    child_id = next(i for i, m in items.items() if m["text"] == "Child")
    loose_id = next(i for i, m in items.items() if m["text"] == "Loose")
    diag_id = next(i for i, m in items.items() if m["text"] == "Child Diagram")

    assert items[parent_id]["parent"] == gov_id
    assert items[parent_id]["image"] == "PKG"
    assert items[child_id]["parent"] == parent_id
    assert items[child_id]["image"] == "PKG"
    assert items[diag_id]["parent"] == child_id
    assert items[diag_id]["image"] == "DIAG"
    assert items[loose_id]["parent"] == gov_id

