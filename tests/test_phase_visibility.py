from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from dataclasses import asdict
import types
import sys
from gui.architecture import SysMLObject, DiagramConnection, SysMLDiagramWindow

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

def test_elements_follow_phase_visibility():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1"), GovernanceModule("P2")]
    toolbox.set_active_module("P1")
    elem = repo.create_element("Block")
    assert repo.element_visible(elem.elem_id)
    assert elem.phase == "P1"
    visible = set(repo.visible_elements().keys())
    assert elem.elem_id in visible
    toolbox.set_active_module("P2")
    assert not repo.element_visible(elem.elem_id)
    visible = set(repo.visible_elements().keys())
    assert elem.elem_id not in visible
    toolbox.set_active_module("P1")
    assert repo.element_visible(elem.elem_id)
    visible = set(repo.visible_elements().keys())
    assert elem.elem_id in visible


def test_diagram_objects_and_connections_follow_phase_visibility():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1"), GovernanceModule("P2")]
    toolbox.set_active_module("P1")
    diag = repo.create_diagram("Block Definition Diagram")
    obj = SysMLObject(1, "Block", 0.0, 0.0)
    diag.objects.append(asdict(obj))
    conn = DiagramConnection(1, 2, "Association")
    diag.connections.append(asdict(conn))
    assert repo.visible_objects(diag.diag_id)
    assert repo.visible_connections(diag.diag_id)


def test_diagram_window_respects_phase():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1"), GovernanceModule("P2")]
    toolbox.set_active_module("P1")
    diag = repo.create_diagram("Block Definition Diagram")
    obj = SysMLObject(1, "Block", 0.0, 0.0)
    diag.objects.append(asdict(obj))
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.sort_objects = lambda: None
    win.redraw = lambda: None
    win.update_property_view = lambda: None
    SysMLDiagramWindow.refresh_from_repository(win)
    assert len(win.objects) == 1
    toolbox.set_active_module("P2")
    SysMLDiagramWindow.refresh_from_repository(win)
    assert len(win.objects) == 0


def test_on_lifecycle_selected_refreshes_diagrams():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1")]
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.lifecycle_var = types.SimpleNamespace(get=lambda: "P1")
    app.safety_mgmt_toolbox = toolbox
    refreshed = {"count": 0}

    class DummyChild:
        def refresh_from_repository(self):
            refreshed["count"] += 1

    class DummyTab:
        def __init__(self):
            self.child = DummyChild()

        def winfo_children(self):
            return [self.child]

    app.diagram_tabs = {"d": DummyTab()}
    app.update_views = lambda: None
    app.refresh_tool_enablement = lambda: None
    app.on_lifecycle_selected = FaultTreeApp.on_lifecycle_selected.__get__(app, FaultTreeApp)
    app.on_lifecycle_selected()
    assert refreshed["count"] == 1
