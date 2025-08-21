import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from sysml.sysml_repository import SysMLRepository
import math


def test_work_product_clamped_to_process_area():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.app = None

    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 0.0, 0.0, area=area)

    wp.x = area.x + area.width
    wp.y = area.y + area.height
    win._constrain_to_parent(wp)

    assert win.find_boundary_for_obj(wp) == area
    right = area.x + area.width / 2 - wp.width / 2
    bottom = area.y + area.height / 2 - wp.height / 2
    assert math.isclose(wp.x, right)
    assert math.isclose(wp.y, bottom)
    assert wp.properties.get("px") == str(wp.x - area.x)
    assert wp.properties.get("py") == str(wp.y - area.y)


def test_add_work_product_existing_area_click():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.app = None

    area = win._place_process_area("Risk Assessment", 10.0, 10.0)

    class DummyCanvas:
        def canvasx(self, x):
            return x

        def canvasy(self, y):
            return y

        def configure(self, **kwargs):
            pass

    win.canvas = DummyCanvas()

    called = {"process": 0}

    def _select_process_area():
        called["process"] += 1
        return "Risk Assessment"

    def _select_wp(area_name):
        assert area_name == "Risk Assessment"
        return "Risk Assessment"

    win._select_process_area = _select_process_area
    win._select_work_product_for_area = _select_wp

    win.add_work_product()

    class Event:
        x = 10
        y = 10

    win.on_left_press(Event())

    assert called["process"] == 0
    wps = [o for o in win.objects if o.obj_type == "Work Product"]
    assert len(wps) == 1
    assert wps[0].properties.get("parent") == str(area.obj_id)


def test_right_click_process_area_adds_work_product():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.app = None

    area = win._place_process_area("Risk Assessment", 5.0, 5.0)

    class DummyCanvas:
        def canvasx(self, x):
            return x

        def canvasy(self, y):
            return y

    win.canvas = DummyCanvas()
    win.rc_dragged = False

    def _select_wp(area_name):
        assert area_name == "Risk Assessment"
        return "Risk Assessment"

    win._select_work_product_for_area = _select_wp

    class Event:
        x = 5
        y = 5

    win.on_rc_release(Event())

    wps = [o for o in win.objects if o.obj_type == "Work Product"]
    assert len(wps) == 1
    assert wps[0].properties.get("parent") == str(area.obj_id)


def test_process_area_drag_moves_work_product():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.app = None

    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 10.0, 0.0, area=area)

    class DummyCanvas:
        def canvasx(self, x):
            return x

        def canvasy(self, y):
            return y

    win.canvas = DummyCanvas()
    win.selected_obj = area
    win.current_tool = "Select"
    win.drag_offset = (0, 0)
    win.start = None
    win.select_rect_start = None
    win.dragging_conn_mid = None
    win.selected_conn = None
    win.dragging_endpoint = None
    win.dragging_point_index = None
    win.resizing_obj = None

    class Event:
        x = 100
        y = 50

    win.on_left_drag(Event())

    assert win.find_boundary_for_obj(wp) == area
    assert wp.x == area.x + 10
    assert wp.y == area.y
    assert wp.properties.get("px") == "10.0"
    assert wp.properties.get("py") == "0.0"


def test_process_area_multiple_drags_keep_work_product_offset():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.app = None

    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 10.0, 0.0, area=area)

    class DummyCanvas:
        def canvasx(self, x):
            return x

        def canvasy(self, y):
            return y

    win.canvas = DummyCanvas()
    win.selected_obj = area
    win.current_tool = "Select"
    win.drag_offset = (5, 10)
    win.start = None
    win.select_rect_start = None
    win.dragging_conn_mid = None
    win.selected_conn = None
    win.dragging_endpoint = None
    win.dragging_point_index = None
    win.resizing_obj = None

    class Event1:
        x = 105
        y = 60

    win.on_left_drag(Event1())

    win.drag_offset = (5, 10)

    class Event2:
        x = 165
        y = 90

    win.on_left_drag(Event2())

    assert win.find_boundary_for_obj(wp) == area
    assert wp.x == area.x + 10
    assert wp.y == area.y
    assert wp.properties.get("px") == "10.0"
    assert wp.properties.get("py") == "0.0"
