import os
import sys
from types import SimpleNamespace

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis.models import REQUIREMENT_WORK_PRODUCTS
from gui.architecture import SysMLDiagramWindow, SysMLObject
import gui.architecture as arch
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def configure(self, **kwargs):
        pass


def _make_window(tool):
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    diag = SysMLDiagram(diag_id="d", diag_type="Governance Diagram")
    repo.diagrams["d"] = diag

    window = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    window.canvas = DummyCanvas()
    window.zoom = 1.0
    window.repo = repo
    window.diagram_id = "d"
    window.current_tool = tool
    window.selected_obj = None
    window.selected_conn = None
    window.selected_objs = []
    window.start = None
    window.connections = diag.connections

    wp1, wp2 = REQUIREMENT_WORK_PRODUCTS[:2]
    obj1 = SysMLObject(1, "Work Product", 0, 0, properties={"name": wp1})
    obj2 = SysMLObject(2, "Work Product", 100, 0, properties={"name": wp2})
    diag.objects = [obj1, obj2]
    window.objects = diag.objects

    window.find_connection = lambda x, y: None
    window.find_object = lambda x, y, prefer_port=False: obj1 if x < 50 else obj2
    window.hit_compartment_toggle = lambda o, x, y: None
    window.update_property_view = lambda: None
    window.redraw = lambda: None
    window._sync_to_repository = lambda: None
    window.validate_connection = SysMLDiagramWindow.validate_connection.__get__(window)
    window.get_object = lambda oid: obj1 if oid == 1 else obj2

    arch.ConnectionDialog = lambda *a, **k: None

    return window, obj1, obj2


def test_requirement_relation_tool_creates_connection():
    for tool in ("Satisfied by", "Derived from"):
        window, obj1, obj2 = _make_window(tool)
        window.on_left_press(SimpleNamespace(x=0, y=0, state=0))
        assert len(window.objects) == 2
        assert window.start == obj1

        window.on_left_press(SimpleNamespace(x=100, y=0, state=0))
        assert len(window.connections) == 1
        conn = window.connections[0]
        assert conn.conn_type == tool
        assert all(o.obj_type != tool for o in window.objects)
