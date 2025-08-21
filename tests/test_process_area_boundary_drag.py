import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from sysml.sysml_repository import SysMLRepository


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def delete(self, *args, **kwargs):
        pass

    def configure(self, **kwargs):
        pass


class DummyEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def _setup_window():
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
    win.canvas = DummyCanvas()
    win.app = None
    win.start = None
    win.select_rect_start = None
    win.dragging_conn_mid = None
    win.selected_conn = None
    win.dragging_endpoint = None
    win.dragging_point_index = None
    win.conn_drag_offset = None
    win.endpoint_drag_pos = None
    win.current_tool = "Select"
    win.drag_offset = (0, 0)
    win.resizing_obj = None
    win.selected_obj = None
    win._constrain_horizontal_movement = GovernanceDiagramWindow._constrain_horizontal_movement.__get__(win)
    win.get_object = GovernanceDiagramWindow.get_object.__get__(win)
    win.get_ibd_boundary = GovernanceDiagramWindow.get_ibd_boundary.__get__(win)
    win.find_boundary_for_obj = GovernanceDiagramWindow.find_boundary_for_obj.__get__(win)
    win._object_within = GovernanceDiagramWindow._object_within.__get__(win)
    return win


def test_work_product_offset_persists_on_boundary_move():
    win = _setup_window()
    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 3.3, 3.7, area=area)
    px_before = wp.properties["px"]
    py_before = wp.properties["py"]
    win.selected_obj = area
    win.on_left_drag(DummyEvent(200, 200))
    win.on_left_release(DummyEvent(200, 200))
    assert wp.properties["px"] == px_before
    assert wp.properties["py"] == py_before
