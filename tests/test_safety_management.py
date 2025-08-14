import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import types
import sys
import tkinter as tk

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
from analysis.safety_management import (
    SafetyManagementToolbox,
    GovernanceModule,
    SafetyWorkProduct,
)
from gui.architecture import GovernanceDiagramWindow, SysMLObject, ArchitectureManagerDialog
from gui.safety_management_explorer import SafetyManagementExplorer
from gui.safety_management_toolbox import SafetyManagementWindow
from gui.review_toolbox import ReviewData
from sysml.sysml_repository import SysMLRepository
from tkinter import simpledialog
from analysis.models import HazopDoc, StpaDoc


def test_work_product_registration():
    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("Governance Diagram", "HAZOP", "Link action to hazard")

    products = toolbox.get_work_products()
    assert len(products) == 1
    assert products[0].diagram == "Governance Diagram"
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
        self.rect_calls = []
        self.polygon_calls = []
        self.line_calls = []

    def create_text(self, x, y, **kw):
        self.text_calls.append((x, y, kw))

    def create_rectangle(self, *args, **kwargs):
        self.rect_calls.append((args, kwargs))

    def create_line(self, *args, **kwargs):
        self.line_calls.append((args, kwargs))

    def create_polygon(self, *args, **kwargs):
        self.polygon_calls.append((args, kwargs))

    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y


def test_activity_boundary_label_rotated_left_inside():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.zoom = 1.0
    win.canvas = DummyCanvas()
    win.font = None
    win._draw_gradient_rect = lambda *args, **kwargs: None
    win.selected_objs = []
    long_name = "Very Long Process Area Name"
    obj = SysMLObject(
        1,
        "System Boundary",
        0.0,
        0.0,
        width=100.0,
        height=80.0,
        properties={"name": long_name},
    )
    win.draw_object(obj)

    assert win.canvas.text_calls, "label not drawn"
    x, y, kwargs = win.canvas.text_calls[0]
    assert kwargs.get("angle") == 90
    assert kwargs.get("anchor") == "w"
    assert "\n" in kwargs.get("text", ""), "label not wrapped inside boundary"
    assert x == obj.x - obj.width / 2 + 8
    assert y == obj.y
    # compartment line drawn to separate title
    assert win.canvas.line_calls, "compartment not drawn"
    (line_args, _line_kwargs) = win.canvas.line_calls[0]
    x1, y1, x2, y2 = line_args
    assert x1 == x2
    lines = kwargs.get("text", "").count("\n") + 1
    expected_x = x + lines * 16 + 8
    assert x1 == expected_x


def test_process_area_boundary_title_clipped_inside():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.zoom = 1.0
    win.canvas = DummyCanvas()
    win.font = None
    win._draw_gradient_rect = lambda *args, **kwargs: None
    win.selected_objs = []
    long_name = "A" * 200
    obj = SysMLObject(
        1,
        "System Boundary",
        0.0,
        0.0,
        width=100.0,
        height=80.0,
        properties={"name": long_name},
    )
    win.draw_object(obj)

    assert win.canvas.text_calls, "label not drawn"
    x, _y, kwargs = win.canvas.text_calls[0]
    right = obj.x + obj.width / 2
    (line_args, _line_kwargs) = win.canvas.line_calls[0]
    x1, _y1, x2, _y2 = line_args
    assert x1 == x2
    assert x1 <= right, "compartment line extends beyond boundary"
    assert "\n" in kwargs.get("text", "")
    max_lines = 5
    assert kwargs["text"].count("\n") + 1 <= max_lines


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


def test_sync_diagrams_updates_module_references():
    """Renamed diagrams should update module references and avoid duplicates."""
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    diag_id = toolbox.create_diagram("Orig")
    toolbox.modules = [GovernanceModule("Mod1", diagrams=["Orig"])]

    # Rename the diagram directly in the repository to simulate external change
    repo.diagrams[diag_id].name = "Renamed"

    # Trigger a sync and ensure the module reflects the new name
    toolbox.list_diagrams()
    assert toolbox.modules[0].diagrams == ["Renamed"]
    assert "Orig" not in toolbox.diagrams


def test_rename_module_updates_active():
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("Phase1")]
    toolbox.set_active_module("Phase1")
    toolbox.rename_module("Phase1", "PhaseX")
    assert toolbox.modules[0].name == "PhaseX"
    assert toolbox.active_module == "PhaseX"


def test_disable_work_product_rejects_existing_docs():
    """Work product types with existing documents cannot be removed."""
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.enabled_work_products = {"HAZOP"}
    app.work_product_menus = {}
    app.tool_listboxes = {}
    app.tool_actions = {}
    app.hazop_docs = [object()]
    assert not app.disable_work_product("HAZOP")

    # When no documents exist the work product can be disabled
    class DummyMenu:
        def __init__(self):
            self.state = None

        def entryconfig(self, idx, state=tk.DISABLED):
            self.state = state

    menu = DummyMenu()
    app.hazop_docs = []
    app.work_product_menus["HAZOP"] = [(menu, 0)]
    assert app.disable_work_product("HAZOP")
    assert menu.state == tk.DISABLED


def test_open_safety_management_toolbox_uses_browser():
    """FaultTreeApp opens the Safety & Security Management window and toolbox."""
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


def test_work_product_enabling_and_deletion_guard():
    """Governance diagrams enable work products and prevent unsafe removal."""
    toolbox = SafetyManagementToolbox()

    # HAZOP creation disabled until explicitly registered
    assert not toolbox.is_enabled("HAZOP")

    toolbox.add_work_product("Gov", "HAZOP", "Link action to hazard")
    assert toolbox.is_enabled("HAZOP")

    # An existing document blocks removal of the work product declaration
    toolbox.register_created_work_product("HAZOP", "Doc1")
    removed = toolbox.remove_work_product("Gov", "HAZOP")
    assert removed is False

    # After deleting the document removal succeeds
    toolbox.register_deleted_work_product("HAZOP", "Doc1")
    removed = toolbox.remove_work_product("Gov", "HAZOP")
    assert removed is True
    assert not toolbox.is_enabled("HAZOP")

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
    assert "Safety & Security Management" in texts
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


def test_explorers_removed_from_safety_concept_group():
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

        def insert(self, parent, index, iid=None, text="", tags=(), **kwargs):
            if iid is None:
                iid = f"i{self.counter}"
                self.counter += 1
            self.items[iid] = {"parent": parent, "text": text, "tags": tags}
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
    assert "Safety & Security Management Explorer" not in texts
    assert "GSN Explorer" not in texts


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
    diag = repo.create_diagram("Governance Diagram", name="GovX")
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


def test_enabled_products_filter_by_module():
    toolbox = SafetyManagementToolbox()
    toolbox.diagrams = {"D1": "id1", "D2": "id2"}
    toolbox.work_products = [
        SafetyWorkProduct("D1", "HAZOP", ""),
        SafetyWorkProduct("D2", "FTA", ""),
    ]
    toolbox.modules = [
        GovernanceModule(name="Phase1", diagrams=["D1"]),
        GovernanceModule(name="Phase2", diagrams=["D2"]),
    ]

    toolbox.set_active_module("Phase1")
    assert toolbox.enabled_products() == {"HAZOP"}

    toolbox.set_active_module("Phase2")
    assert toolbox.enabled_products() == {"FTA"}

    toolbox.set_active_module(None)
    assert toolbox.enabled_products() == set()


def test_disabled_work_products_absent_from_analysis_tree():
    SysMLRepository._instance = None
    SysMLRepository.get_instance()

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0

        def delete(self, *items):
            self.items.clear()

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
    app.arch_diagrams = []
    app.management_diagrams = []
    app.gsn_diagrams = []
    app.gsn_modules = []
    app.reviews = []
    app.enabled_work_products = set()
    app.analysis_tree = DummyTree()
    app.update_views()
    texts = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert "Hazard & Threat Analysis" not in texts
    assert "Risk Assessment" not in texts
    assert "Safety Analysis" not in texts

    app.enabled_work_products = {"HAZOP"}
    app.analysis_tree = DummyTree()
    app.update_views()
    texts = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert "Hazard & Threat Analysis" in texts
    assert "HAZOPs" in texts


def test_enable_work_product_refreshes_views():
    app = FaultTreeApp.__new__(FaultTreeApp)
    called = {"count": 0}
    app.update_views = lambda: called.__setitem__("count", called["count"] + 1)
    app.tool_listboxes = {}
    app.tool_categories = {}
    app.work_product_menus = {}
    app.tool_actions = {}
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    FaultTreeApp.enable_work_product(app, "HAZOP")
    assert called["count"] == 1
    app.hazop_docs = []
    FaultTreeApp.disable_work_product(app, "HAZOP")
    assert called["count"] == 2


def test_open_work_product_requires_enablement():
    app = FaultTreeApp.__new__(FaultTreeApp)
    opened = {"count": 0}
    app.tool_actions = {"HAZOP Analysis": lambda: opened.__setitem__("count", opened["count"] + 1)}
    app.arch_diagrams = []
    app.management_diagrams = []
    app.all_gsn_diagrams = []
    app.enabled_work_products = set()
    app.open_work_product("HAZOP Analysis")
    assert opened["count"] == 0
    app.enabled_work_products.add("HAZOP")
    app.open_work_product("HAZOP Analysis")
    assert opened["count"] == 1


def test_phase_without_diagrams_disables_products():
    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("Gov1", "HAZOP", "link")
    toolbox.modules = [GovernanceModule(name="P1")]
    toolbox.set_active_module("P1")
    assert toolbox.enabled_products() == set()


def test_menu_work_products_toggle_and_guard_existing_docs():
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.tool_listboxes = {}
    app.tool_categories = {}
    app.tool_actions = {}
    app.enable_process_area = lambda area: None

    class DummyMenu:
        def __init__(self):
            self.state = None

        def entryconfig(self, idx, state=tk.DISABLED):
            self.state = state

    cases = [
        ("Process", None),
        ("Quantitative Analysis", "fmeas"),
        ("Qualitative Analysis", "hazop_docs"),
        ("Architecture Diagram", "arch_diagrams"),
        ("Scenario", "scenario_libraries"),
        ("FTA", "top_events"),
    ]

    for name, attr in cases:
        menu = DummyMenu()
        app.work_product_menus = {name: [(menu, 0)]}
        app.enabled_work_products = set()
        app.tool_actions = {}
        app.tool_listboxes = {}
        app.tool_categories = {}
        if attr:
            setattr(app, attr, [])
        FaultTreeApp.enable_work_product(app, name)
        assert menu.state == tk.NORMAL
        if attr:
            getattr(app, attr).append(object())
            assert not FaultTreeApp.disable_work_product(app, name)
            assert menu.state == tk.NORMAL
            getattr(app, attr).clear()
        assert FaultTreeApp.disable_work_product(app, name)
        assert menu.state == tk.DISABLED

def test_governance_diagram_opens_with_governance_toolbox(monkeypatch):
    """Governance diagrams open as Governance diagrams with their toolbox."""
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="GovA")
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

    calls = {"governance": False, "activity": False}

    def fake_governance(tab, _app, diagram_id):
        calls["governance"] = True
        assert diagram_id == diag.diag_id

    def fake_activity(tab, _app, diagram_id):
        calls["activity"] = True

    monkeypatch.setattr(AutoML, "GovernanceDiagramWindow", fake_governance)
    monkeypatch.setattr(AutoML, "ActivityDiagramWindow", fake_activity)

    app.open_management_window(0)

    assert calls["governance"]
    assert not calls["activity"]


def test_diagram_hierarchy_orders_levels():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    a = repo.create_diagram("Governance Diagram", name="A")
    b = repo.create_diagram("Governance Diagram", name="B")
    c = repo.create_diagram("Governance Diagram", name="C")
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

    parent = repo.create_diagram("Governance Diagram", name="Parent")
    child = repo.create_diagram("Governance Diagram", name="Child")
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


def test_work_products_filtered_by_phase_in_tree():
    """Documents appear only when their creation phase is active."""
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()

    d1 = repo.create_diagram("Governance Diagram", name="Gov1")
    d2 = repo.create_diagram("Governance Diagram", name="Gov2")
    for d in (d1, d2):
        d.tags.append("safety-management")

    toolbox = SafetyManagementToolbox()
    toolbox.list_diagrams()
    toolbox.modules = [
        GovernanceModule(name="P1", diagrams=["Gov1"]),
        GovernanceModule(name="P2", diagrams=["Gov2"]),
    ]

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0

        def delete(self, *items):
            self.items = {}

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
    app.hazop_docs = [HazopDoc("HZ1", []), HazopDoc("HZ2", [])]
    app.stpa_docs = [StpaDoc("S1", "", []), StpaDoc("S2", "", [])]
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hara_docs = []
    app.top_events = []
    app.fmeas = []
    app.fmedas = []
    app.tool_listboxes = {}
    app.analysis_tree = DummyTree()
    app.safety_mgmt_toolbox = toolbox

    class DummyVar:
        def __init__(self, value=""):
            self.value = value

        def get(self):
            return self.value

        def set(self, value):
            self.value = value

    app.lifecycle_var = DummyVar("P1")
    app.on_lifecycle_selected()
    toolbox.register_created_work_product("HAZOP", "HZ1")
    toolbox.register_created_work_product("STPA", "S1")
    app.lifecycle_var.set("P2")
    app.on_lifecycle_selected()
    toolbox.register_created_work_product("HAZOP", "HZ2")
    toolbox.register_created_work_product("STPA", "S2")

    app.lifecycle_var.set("P1")
    app.on_lifecycle_selected()
    names = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert "HZ1" in names and "HZ2" not in names
    assert "S1" in names and "S2" not in names

    app.lifecycle_var.set("P2")
    app.on_lifecycle_selected()
    names = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert "HZ2" in names and "HZ1" not in names
    assert "S2" in names and "S1" not in names


def test_governance_enables_tools_per_phase():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    d1 = repo.create_diagram("Governance Diagram", name="Gov1")
    d2 = repo.create_diagram("Governance Diagram", name="Gov2")
    for d in (d1, d2):
        d.tags.append("safety-management")

    toolbox = SafetyManagementToolbox()
    toolbox.list_diagrams()
    toolbox.modules = [
        GovernanceModule(name="P1", diagrams=["Gov1"]),
        GovernanceModule(name="P2", diagrams=["Gov2"]),
    ]

    class DummyListbox:
        def __init__(self):
            self.items: list[str] = []
            self.colors: list[str] = []

        def get(self, *args):
            if len(args) == 1:
                return self.items[args[0]]
            return list(self.items)

        def insert(self, _index, item):
            self.items.append(item)
            self.colors.append("black")

        def itemconfig(self, index, foreground="black"):
            self.colors[index] = foreground

        def size(self):
            return len(self.items)

        def delete(self, index):
            del self.items[index]
            del self.colors[index]

    class DummyMenu:
        def __init__(self):
            self.state = None

        def entryconfig(self, _idx, state=tk.DISABLED):
            self.state = state

    class DummyVar:
        def __init__(self, value=""):
            self.value = value

        def get(self):
            return self.value

        def set(self, value):
            self.value = value

    app = FaultTreeApp.__new__(FaultTreeApp)
    lb = DummyListbox()
    menu_arch = DummyMenu()
    menu_req = DummyMenu()
    app.tool_listboxes = {"System Design (Item Definition)": lb}
    app.tool_categories = {"System Design (Item Definition)": []}
    app.tool_actions = {}
    app.work_product_menus = {
        "Architecture Diagram": [(menu_arch, 0)],
        "Requirement Specification": [(menu_req, 0)],
    }
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.manage_architecture = lambda: None
    app.show_requirements_editor = lambda: None
    app.tool_to_work_product = {
        info[1]: name for name, info in FaultTreeApp.WORK_PRODUCT_INFO.items()
    }
    app.update_views = lambda: None
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(
        app, FaultTreeApp
    )
    app.enable_work_product = FaultTreeApp.enable_work_product.__get__(
        app, FaultTreeApp
    )
    app.disable_work_product = FaultTreeApp.disable_work_product.__get__(
        app, FaultTreeApp
    )
    app.on_lifecycle_selected = FaultTreeApp.on_lifecycle_selected.__get__(
        app, FaultTreeApp
    )
    app.safety_mgmt_toolbox = toolbox
    toolbox.on_change = app.refresh_tool_enablement

    toolbox.add_work_product("Gov1", "Architecture Diagram", "r")
    toolbox.add_work_product("Gov2", "Requirement Specification", "r")
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("Architecture Diagram", "Arch1")
    toolbox.set_active_module("P2")
    toolbox.register_created_work_product("Requirement Specification", "Req1")
    toolbox.set_active_module(None)

    app.lifecycle_var = DummyVar("P1")
    app.on_lifecycle_selected()
    assert menu_arch.state == tk.NORMAL and menu_req.state == tk.DISABLED
    assert lb.items == ["AutoML Explorer"]
    assert lb.colors == ["black"]

    app.lifecycle_var.set("P2")
    app.on_lifecycle_selected()
    assert menu_arch.state == tk.DISABLED and menu_req.state == tk.NORMAL
    assert lb.items == ["Requirements Editor"]
    assert lb.colors == ["black"]

    app.lifecycle_var.set("P1")
    app.on_lifecycle_selected()
    assert menu_arch.state == tk.NORMAL and menu_req.state == tk.DISABLED
    assert lb.items == ["AutoML Explorer"]
    assert lb.colors == ["black"]


def test_phase_selection_updates_app(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov1"])]
    toolbox.diagrams = {"Gov1": diag.diag_id}

    class DummyVar:
        def __init__(self, value=""):
            self.value = value

        def get(self):
            return self.value

        def set(self, value):
            self.value = value

    app = types.SimpleNamespace(lifecycle_var=DummyVar(), called=False)

    def on_lifecycle_selected(_event=None):
        app.called = True

    app.on_lifecycle_selected = on_lifecycle_selected

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = app
    win.phase_var = DummyVar("P1")
    win.refresh_diagrams = lambda: None

    SafetyManagementWindow.select_phase(win)

    assert toolbox.active_module == "P1"
    assert app.lifecycle_var.get() == "P1"
    assert app.called


def test_phase_selection_refreshes_menus():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov1"])]
    toolbox.diagrams = {"Gov1": diag.diag_id}

    class DummyVar:
        def __init__(self, value=""):
            self.value = value

        def get(self):
            return self.value

        def set(self, value):
            self.value = value

    class DummyMenu:
        def __init__(self):
            self.state = tk.DISABLED

        def entryconfig(self, _idx, state=tk.DISABLED):
            self.state = state

    menu = DummyMenu()
    app = types.SimpleNamespace(
        lifecycle_var=DummyVar(),
        work_product_menus={"HAZOP": [(menu, 0)]},
        enabled_work_products=set(),
        tool_listboxes={},
        safety_mgmt_toolbox=toolbox,
    )

    def refresh_tool_enablement():
        for m, idx in app.work_product_menus["HAZOP"]:
            m.entryconfig(idx, state=tk.NORMAL)

    app.refresh_tool_enablement = refresh_tool_enablement

    def on_lifecycle_selected(_event=None):
        pass

    app.on_lifecycle_selected = on_lifecycle_selected

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = app
    win.phase_var = DummyVar("P1")
    win.refresh_diagrams = lambda: None

    SafetyManagementWindow.select_phase(win)

    assert menu.state == tk.NORMAL


def test_child_work_product_enables_parent_menu():
    """Enabling a work product should also activate its parent menu."""

    class DummyMenu:
        def __init__(self):
            self.state = tk.DISABLED

        def entryconfig(self, _idx, state=tk.DISABLED):
            self.state = state

    parent_menu = DummyMenu()
    child_menu = DummyMenu()

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.tool_listboxes = {}
    app.tool_actions = {}
    app.tool_categories = {}
    app._add_tool_category = lambda area, names: None
    app.work_product_menus = {
        "HAZOP": [(child_menu, 0)],
        "Qualitative Analysis": [(parent_menu, 0)],
    }
    app.enabled_work_products = set()
    app.update_views = lambda: None

    FaultTreeApp.enable_work_product(app, "HAZOP")

    assert child_menu.state == tk.NORMAL
    assert parent_menu.state == tk.NORMAL

    FaultTreeApp.disable_work_product(app, "HAZOP", force=True)
    assert parent_menu.state == tk.DISABLED


def test_refresh_tool_enablement_enables_parent_menus():
    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("Gov1", "HAZOP", "")
    toolbox.add_work_product("Gov1", "FMEDA", "")
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov1"])]
    toolbox.diagrams = {"Gov1": "id"}
    toolbox.set_active_module("P1")

    class DummyMenu:
        def __init__(self):
            self.state = tk.DISABLED

        def entryconfig(self, _idx, state=tk.DISABLED):
            self.state = state

    hazop_menu = DummyMenu()
    qual_menu = DummyMenu()
    fmeda_menu = DummyMenu()
    quant_menu = DummyMenu()

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.tool_listboxes = {}
    app.tool_categories = {}
    app.tool_actions = {}
    app.enable_process_area = lambda area: None
    app.update_views = lambda: None
    app.work_product_menus = {
        "HAZOP": [(hazop_menu, 0)],
        "Qualitative Analysis": [(qual_menu, 0)],
        "FMEDA": [(fmeda_menu, 0)],
        "Quantitative Analysis": [(quant_menu, 0)],
    }
    app.enabled_work_products = set()
    app.safety_mgmt_toolbox = toolbox

    FaultTreeApp.refresh_tool_enablement(app)

    assert hazop_menu.state == tk.NORMAL
    assert qual_menu.state == tk.NORMAL
    assert fmeda_menu.state == tk.NORMAL
    assert quant_menu.state == tk.NORMAL

def test_phase_without_diagrams_disables_tools():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    d1 = repo.create_diagram("Governance Diagram", name="Gov1")
    d1.tags.append("safety-management")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [
        GovernanceModule(name="P1", diagrams=["Gov1"]),
        GovernanceModule(name="P2"),
    ]
    toolbox.diagrams = {"Gov1": d1.diag_id}

    class DummyListbox:
        def __init__(self):
            self.items: list[str] = []
            self.colors: list[str] = []

        def get(self, *args):
            if len(args) == 1:
                return self.items[args[0]]
            return list(self.items)

        def insert(self, _index, item):
            self.items.append(item)
            self.colors.append("black")

        def itemconfig(self, index, foreground="black"):
            self.colors[index] = foreground

        def size(self):
            return len(self.items)

        def delete(self, index):
            del self.items[index]
            del self.colors[index]

    class DummyMenu:
        def __init__(self):
            self.state = None

        def entryconfig(self, _idx, state=tk.DISABLED):
            self.state = state

    class DummyVar:
        def __init__(self, value=""):
            self.value = value

        def get(self):
            return self.value

        def set(self, value):
            self.value = value

    app = FaultTreeApp.__new__(FaultTreeApp)
    lb = DummyListbox()
    menu_arch = DummyMenu()
    app.tool_listboxes = {"System Design (Item Definition)": lb}
    app.tool_categories = {"System Design (Item Definition)": []}
    app.tool_actions = {}
    app.work_product_menus = {"Architecture Diagram": [(menu_arch, 0)]}
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.manage_architecture = lambda: None
    app.tool_to_work_product = {
        info[1]: name for name, info in FaultTreeApp.WORK_PRODUCT_INFO.items()
    }
    app.update_views = lambda: None
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(
        app, FaultTreeApp
    )
    app.enable_work_product = FaultTreeApp.enable_work_product.__get__(
        app, FaultTreeApp
    )
    app.disable_work_product = FaultTreeApp.disable_work_product.__get__(
        app, FaultTreeApp
    )
    app.on_lifecycle_selected = FaultTreeApp.on_lifecycle_selected.__get__(
        app, FaultTreeApp
    )
    app.safety_mgmt_toolbox = toolbox
    toolbox.on_change = app.refresh_tool_enablement

    toolbox.add_work_product("Gov1", "Architecture Diagram", "r")
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("Architecture Diagram", "Arch1")
    toolbox.set_active_module(None)

    app.lifecycle_var = DummyVar("P1")
    app.on_lifecycle_selected()
    assert menu_arch.state == tk.NORMAL
    assert lb.items == ["AutoML Explorer"]

    app.lifecycle_var.set("P2")
    app.on_lifecycle_selected()
    assert menu_arch.state == tk.DISABLED
    assert lb.items == []


def test_governance_without_declarations_keeps_tools_enabled():
    """Tools remain enabled when no work products are declared."""

    toolbox = SafetyManagementToolbox()

    class DummyListbox:
        def __init__(self):
            self.items: list[str] = []
            self.colors: list[str] = []

        def get(self, *args):
            if len(args) == 1:
                return self.items[args[0]]
            return list(self.items)

        def insert(self, _index, item):
            self.items.append(item)
            self.colors.append("black")

        def itemconfig(self, index, foreground="black"):
            self.colors[index] = foreground

    class DummyMenu:
        def __init__(self):
            self.state = None

        def entryconfig(self, _idx, state=tk.DISABLED):
            self.state = state

    app = FaultTreeApp.__new__(FaultTreeApp)
    lb = DummyListbox()
    menu_arch = DummyMenu()
    menu_req = DummyMenu()
    app.tool_listboxes = {"System Design (Item Definition)": lb}
    app.tool_categories = {"System Design (Item Definition)": []}
    app.tool_actions = {}
    app.work_product_menus = {
        "Architecture Diagram": [(menu_arch, 0)],
        "Requirement Specification": [(menu_req, 0)],
    }
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.manage_architecture = lambda: None
    app.show_requirements_editor = lambda: None
    app.tool_to_work_product = {
        info[1]: name for name, info in FaultTreeApp.WORK_PRODUCT_INFO.items()
    }
    app.update_views = lambda: None
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(
        app, FaultTreeApp
    )
    app.enable_work_product = FaultTreeApp.enable_work_product.__get__(
        app, FaultTreeApp
    )
    app.disable_work_product = FaultTreeApp.disable_work_product.__get__(
        app, FaultTreeApp
    )
    app.safety_mgmt_toolbox = toolbox

    app.enable_work_product("Architecture Diagram")
    app.enable_work_product("Requirement Specification")

    app.refresh_tool_enablement()

    assert menu_arch.state == tk.NORMAL and menu_req.state == tk.NORMAL
    assert lb.colors == ["black", "black"]


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


def test_explorer_renames_folders_and_diagrams(monkeypatch):
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
    explorer.app = types.SimpleNamespace(open_arch_window=lambda _id: None)

    SafetyManagementExplorer.populate(explorer)
    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Pkg")
    explorer.new_folder()

    # Find folder iid
    for iid, (typ, obj) in explorer.item_map.items():
        if typ == "module" and obj.name == "Pkg":
            explorer.tree.selection_item = iid
            break

    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Diag")
    explorer.new_diagram()

    # Locate folder iid again after repopulate
    for fid, (typ, obj) in explorer.item_map.items():
        if typ == "module" and obj.name == "Pkg":
            iid = fid
            break

    # Rename folder
    explorer.tree.selection_item = iid
    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "PkgRen")
    explorer.rename_item()
    assert toolbox.modules[0].name == "PkgRen"

    # Find diagram iid and rename
    for di, (typ, obj) in explorer.item_map.items():
        if typ == "diagram" and obj == "Diag":
            explorer.tree.selection_item = di
            break
    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "DiagRen")
    explorer.rename_item()
    assert "DiagRen" in toolbox.modules[0].diagrams
    assert "DiagRen" in toolbox.diagrams


def test_explorer_prevents_diagrams_outside_folders(monkeypatch):
    SysMLRepository._instance = None
    SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    explorer = SafetyManagementExplorer.__new__(SafetyManagementExplorer)

    class DummyTree:
        def selection(self):
            return ()

    explorer.tree = DummyTree()
    explorer.toolbox = toolbox
    explorer.item_map = {}
    explorer.folder_icon = None
    explorer.diagram_icon = None

    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Diag")
    from gui import messagebox as gui_messagebox
    called = {"count": 0}

    def fake_error(*args, **kwargs):
        called["count"] += 1

    monkeypatch.setattr(gui_messagebox, "showerror", fake_error)
    explorer.new_diagram()
    assert not toolbox.diagrams
    assert called["count"] == 1


def test_explorer_allows_diagram_at_root(monkeypatch):
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

        def insert(self, parent, index, text="", image=None, **_kwargs):
            iid = f"i{self.counter}"
            self.counter += 1
            self.items[iid] = {"parent": parent, "text": text}
            return iid

        def selection(self):
            return (self.selection_item,) if self.selection_item else ()

    explorer.tree = DummyTree()
    explorer.toolbox = toolbox
    explorer.item_map = {}
    explorer.folder_icon = None
    explorer.diagram_icon = None

    SafetyManagementExplorer.populate(explorer)
    explorer.tree.selection_item = explorer.root_iid
    monkeypatch.setattr(simpledialog, "askstring", lambda *args, **kwargs: "Diag")
    explorer.new_diagram()
    assert "Diag" in toolbox.diagrams
    assert all("Diag" not in m.diagrams for m in toolbox.modules)


def test_tools_include_safety_management_explorer():
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.manage_safety_management = lambda: None
    app.open_safety_management_toolbox = lambda: None
    app.show_safety_performance_indicators = lambda: None
    app.show_safety_case = lambda: None
    app.manage_gsn = lambda: None

    app.tools = {
        "Safety & Security Management": app.open_safety_management_toolbox,
        "Safety Performance Indicators": app.show_safety_performance_indicators,
        "Safety & Security Case": app.show_safety_case,
        "Safety & Security Management Explorer": app.manage_safety_management,
        "GSN Explorer": app.manage_gsn,
    }
    app.tool_categories = {
        "Safety & Security Management": [
            "Safety & Security Management",
            "Safety & Security Management Explorer",
            "Safety & Security Case",
            "Safety Performance Indicators",
            "GSN Explorer",
        ]
    }

    assert "Safety & Security Management Explorer" in app.tools
    assert "Safety & Security Management Explorer" in app.tool_categories["Safety & Security Management"]


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
    explorer.root_iid = ""
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


def test_folder_double_click_opens_safety_management_explorer():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.create_diagram("Gov1")
    toolbox.modules = [GovernanceModule(name="Folder", diagrams=["Gov1"])]

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0
            self._focus = None

        def delete(self, *items):
            pass

        def insert(self, parent, index, text="", tags=(), image=None, **kwargs):
            iid = f"i{self.counter}"
            self.counter += 1
            self.items[iid] = {"parent": parent, "text": text, "tags": tags}
            if parent in self.items:
                self.items[parent].setdefault("children", []).append(iid)
            return iid

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def item(self, iid, option=None):
            meta = self.items[iid]
            if option == "tags":
                return meta.get("tags", ())
            if option == "text":
                return meta.get("text", "")
            return meta

        def parent(self, iid):
            return self.items[iid]["parent"]

        def focus(self, iid=None):
            if iid is None:
                return self._focus
            self._focus = iid

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
    app.safety_mgmt_toolbox = toolbox

    called = {"explorer": False}
    app.manage_safety_management = lambda: called.__setitem__("explorer", True)

    app.update_views()

    folder_id = next(
        i for i, meta in app.analysis_tree.items.items() if meta["text"] == "Folder"
    )
    app.analysis_tree.focus(folder_id)
    app.on_analysis_tree_double_click(None)

    assert called["explorer"]


def test_add_work_product_uses_half_width(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = [
        SysMLObject(
            2,
            "System Boundary",
            0.0,
            0.0,
            width=200.0,
            height=150.0,
            properties={"name": "Hazard & Threat Analysis"},
        )
    ]
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.app = types.SimpleNamespace(enable_work_product=lambda name, *, refresh=True: None)

    class FakeDialog:
        def __init__(self, *args, **kwargs):
            self.selection = "HAZOP"

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", FakeDialog)

    win.add_work_product()

    wp = [o for o in win.objects if o.obj_type == "Work Product"][0]
    assert wp.width == 60.0


def test_work_product_color_and_text_wrapping():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.zoom = 1.0
    win.canvas = DummyCanvas()
    win.font = None
    win._draw_gradient_rect = lambda *args, **kwargs: None
    win.selected_objs = []

    obj = SysMLObject(
        1,
        "Work Product",
        0.0,
        0.0,
        width=60.0,
        height=80.0,
        properties={"name": "Architecture Diagram"},
    )
    win.draw_object(obj)
    _, poly_kwargs = win.canvas.polygon_calls[0]
    assert poly_kwargs["fill"] == "#cfe2f3"
    assert win.canvas.text_calls[0][2]["width"] == 60.0
    assert win.canvas.text_calls[0][2]["text"] == "Architecture\nDiagram"

    win.canvas.polygon_calls.clear()
    win.canvas.text_calls.clear()
    obj.properties["name"] = "HAZOP"
    win.draw_object(obj)
    _, poly_kwargs = win.canvas.polygon_calls[0]
    assert poly_kwargs["fill"] == "#d5e8d4"


def test_work_product_shapes_fixed_size():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.zoom = 1.0
    win.canvas = DummyCanvas()
    win.start = None
    win.current_tool = "Select"
    win.select_rect_start = None
    win.dragging_endpoint = None
    win.selected_conn = None
    win.dragging_point_index = None
    win.conn_drag_offset = None
    obj = SysMLObject(
        1,
        "Work Product",
        0.0,
        0.0,
        width=60.0,
        height=80.0,
        properties={"name": "HAZOP"},
    )
    win.objects = [obj]
    win.selected_obj = obj
    assert win.hit_resize_handle(obj, 0.0, 0.0) is None
    win.resizing_obj = obj
    win.resize_edge = "se"
    event = types.SimpleNamespace(x=100, y=100)
    win.on_left_drag(event)
    assert obj.width == 60.0
    assert obj.height == 80.0


def test_propagation_connection_validation():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    wp1 = SysMLObject(1, "Work Product", 0.0, 0.0, properties={"name": "Risk Assessment"})
    wp2 = SysMLObject(2, "Work Product", 0.0, 0.0, properties={"name": "FTA"})
    win.objects = [wp1, wp2]
    valid, _ = GovernanceDiagramWindow.validate_connection(win, wp1, wp2, "Propagate")
    assert valid
    wp3 = SysMLObject(3, "Work Product", 0.0, 0.0, properties={"name": "STPA"})
    win.objects.append(wp3)
    valid, _ = GovernanceDiagramWindow.validate_connection(win, wp1, wp3, "Propagate")
    assert not valid


def test_can_propagate_respects_review_states():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams["Gov"] = diag.diag_id
    diag.objects = [
        {"obj_id": 1, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "Risk Assessment"}},
        {"obj_id": 2, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "FTA"}},
    ]
    diag.connections = [{"src": 1, "dst": 2, "conn_type": "Propagate by Review"}]
    assert not toolbox.can_propagate("Risk Assessment", "FTA", reviewed=False)
    assert toolbox.can_propagate("Risk Assessment", "FTA", reviewed=True)
    diag.connections = [{"src": 1, "dst": 2, "conn_type": "Propagate by Approval"}]
    assert not toolbox.can_propagate("Risk Assessment", "FTA", joint_review=False)
    assert toolbox.can_propagate("Risk Assessment", "FTA", joint_review=True)
    diag.connections = [{"src": 1, "dst": 2, "conn_type": "Propagate"}]
    assert toolbox.can_propagate("Risk Assessment", "FTA", reviewed=False)


def test_propagation_type_uses_stereotype_when_conn_type_missing():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams["Gov"] = diag.diag_id
    diag.objects = [
        {"obj_id": 1, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "Risk Assessment"}},
        {"obj_id": 2, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "FTA"}},
    ]
    diag.connections = [{"src": 1, "dst": 2, "stereotype": "propagate by review"}]
    assert toolbox.propagation_type("Risk Assessment", "FTA") == "Propagate by Review"


def test_can_trace_filters_by_phase():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    diag1 = repo.create_diagram("Governance Diagram", name="Gov1")
    diag1.phase = "Phase1"
    toolbox.diagrams["Gov1"] = diag1.diag_id
    diag1.objects = [
        {"obj_id": 1, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "Risk Assessment"}},
        {"obj_id": 2, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "FTA"}},
    ]
    diag1.connections = [{"src": 1, "dst": 2, "conn_type": "Trace"}]

    diag2 = repo.create_diagram("Governance Diagram", name="Gov2")
    diag2.phase = "Phase2"
    toolbox.diagrams["Gov2"] = diag2.diag_id
    diag2.objects = [
        {"obj_id": 1, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "Risk Assessment"}},
        {"obj_id": 2, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "STPA"}},
    ]
    diag2.connections = [{"src": 1, "dst": 2, "conn_type": "Trace"}]

    repo.active_phase = "Phase1"
    toolbox.add_work_product("Gov1", "Risk Assessment", "")
    toolbox.add_work_product("Gov1", "FTA", "")
    toolbox.add_work_product("Gov2", "STPA", "")

    wps = {wp.analysis: wp for wp in toolbox.get_work_products()}
    assert "FTA" in wps["Risk Assessment"].traceable
    assert "STPA" not in wps["Risk Assessment"].traceable
    assert toolbox.can_trace("Risk Assessment", "FTA")
    assert not toolbox.can_trace("Risk Assessment", "STPA")


def test_list_modules_includes_submodules():
    toolbox = SafetyManagementToolbox()
    child = GovernanceModule("Child")
    parent = GovernanceModule("Parent", modules=[child])
    toolbox.modules = [parent]
    assert set(toolbox.list_modules()) == {"Parent", "Child"}


def test_active_module_filters_enabled_products():
    toolbox = SafetyManagementToolbox()
    toolbox.work_products = [
        SafetyWorkProduct("D1", "HAZOP", ""),
        SafetyWorkProduct("D2", "FMEA", ""),
    ]
    toolbox.modules = [
        GovernanceModule("Phase1", diagrams=["D1"]),
        GovernanceModule("Phase2", diagrams=["D2"]),
    ]

    assert toolbox.enabled_products() == set()
    toolbox.set_active_module("Phase1")
    assert toolbox.enabled_products() == {"HAZOP"}
    toolbox.set_active_module(None)
    assert toolbox.enabled_products() == set()


def test_work_product_info_includes_requirement_types():
    for wp in REQUIREMENT_WORK_PRODUCTS:
        assert wp in FaultTreeApp.WORK_PRODUCT_INFO


def test_disable_requirement_work_product_keeps_editor():
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.update_views = lambda: None
    app.tool_listboxes = {}
    app.tool_categories = {}
    app.work_product_menus = {}
    app.tool_actions = {}
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None

    wp1, wp2 = REQUIREMENT_WORK_PRODUCTS[:2]
    FaultTreeApp.enable_work_product(app, wp1)
    FaultTreeApp.enable_work_product(app, wp2)
    assert "Requirements Editor" in app.tool_actions
    FaultTreeApp.disable_work_product(app, wp1)
    assert "Requirements Editor" in app.tool_actions
    FaultTreeApp.disable_work_product(app, wp2)
    assert "Requirements Editor" not in app.tool_actions


def test_focus_governance_diagram_sets_phase_and_hides_functions():
    SysMLRepository._instance = None
    toolbox = SafetyManagementToolbox()
    d1 = toolbox.create_diagram("Gov1")
    d2 = toolbox.create_diagram("Gov2")
    toolbox.modules = [
        GovernanceModule("Phase1", diagrams=["Gov1"]),
        GovernanceModule("Phase2", diagrams=["Gov2"]),
    ]

    class DummyNotebook:
        def __init__(self, app):
            self.app = app
            self._tabs = []
            self._selected = None

        def tabs(self):
            return list(self._tabs)

        def add(self, tab, text=""):
            self._tabs.append(tab)

        def select(self, tab=None):
            if tab is None:
                return self._selected
            self._selected = tab
            self.app._on_tab_change(types.SimpleNamespace(widget=self))

        def nametowidget(self, widget):
            return widget

    class DummyTab:
        def winfo_exists(self):
            return True

        def winfo_children(self):
            return []

    def _new_tab(self, _title):
        tab = DummyTab()
        self.doc_nb.add(tab, text=_title)
        return tab

    def _fmt(self, diag):
        return diag.name or diag.diag_id

    class DummyVar:
        def __init__(self):
            self.value = ""

        def set(self, v):
            self.value = v

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.diagram_tabs = {}
    app.doc_nb = DummyNotebook(app)
    app._new_tab = types.MethodType(_new_tab, app)
    app._format_diag_title = types.MethodType(_fmt, app)
    app.refresh_all = types.MethodType(lambda self: None, app)
    app.lifecycle_var = DummyVar()
    app.safety_mgmt_toolbox = toolbox
    changes: list[str] = []
    toolbox.on_change = lambda: changes.append("x")
    AutoML.GovernanceDiagramWindow = lambda *args, **kwargs: None

    FaultTreeApp.open_arch_window(app, d1)
    app.doc_nb.select(app.diagram_tabs[d1])
    assert toolbox.active_module == "Phase1"
    assert app.lifecycle_var.value == "Phase1"

    FaultTreeApp.open_arch_window(app, d2)
    app.doc_nb.select(app.diagram_tabs[d2])
    assert toolbox.active_module == "Phase2"
    assert app.lifecycle_var.value == "Phase2"

    app.doc_nb.select(app.diagram_tabs[d1])
    assert toolbox.active_module == "Phase1"
    assert app.lifecycle_var.value == "Phase1"
    assert len(changes) == 3
