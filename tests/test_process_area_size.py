import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class DummyFont:
    def measure(self, text):
        return len(text) * 7

    def metrics(self, key):
        return 10


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y


def _basic_window():
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
    win.font = DummyFont()
    win.canvas = DummyCanvas()
    win.app = None
    return win


def test_process_area_resizing_clamps_to_children():
    win = _basic_window()
    area = win._place_process_area("Area", 0.0, 0.0)
    wp = win._place_work_product("WP", 40.0, 0.0, area=area)
    win.selected_obj = area
    win.resizing_obj = area
    win.resize_edge = "e"
    win.current_tool = "Select"
    win.drag_offset = (0, 0)
    win.start = None
    win.select_rect_start = None
    win.dragging_conn_mid = None
    win.selected_conn = None
    win.dragging_endpoint = None
    win.dragging_point_index = None

    class Event:
        x = -50
        y = 0

    win.on_left_drag(Event())
    assert win._object_within(wp, area)


def test_process_area_resizing_keeps_text_visible():
    win = _basic_window()
    name = "VeryLongName"
    area = win._place_process_area(name, 0.0, 0.0)
    win.selected_obj = area
    win.resizing_obj = area
    win.resize_edge = "w"
    win.current_tool = "Select"
    win.drag_offset = (0, 0)
    win.start = None
    win.select_rect_start = None
    win.dragging_conn_mid = None
    win.selected_conn = None
    win.dragging_endpoint = None
    win.dragging_point_index = None

    class Event:
        x = 90
        y = 0

    win.on_left_drag(Event())
    min_width = (win.font.measure(name) + 8 * win.zoom) / win.zoom
    assert area.width >= min_width
