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
from analysis import SafetyManagementToolbox
from gui.architecture import ActivityDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


def test_work_product_registration():
    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("Activity Diagram", "HAZOP", "Link action to hazard")
    products = toolbox.get_work_products()
    assert len(products) == 1
    assert products[0].diagram == "Activity Diagram"
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
    diag = repo.create_diagram("Activity Diagram")
    win = ActivityDiagramWindow.__new__(ActivityDiagramWindow)
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
    """Toolbox creates tagged diagrams and can delete them."""
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    diag_id = toolbox.create_diagram("Gov1")
    assert diag_id in repo.diagrams
    assert "safety-management" in repo.diagrams[diag_id].tags
    assert not hasattr(toolbox, "rename_diagram")

    toolbox.delete_diagram("Gov1")
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
