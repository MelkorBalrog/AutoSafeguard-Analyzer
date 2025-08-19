import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from sysml.sysml_repository import SysMLRepository


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
