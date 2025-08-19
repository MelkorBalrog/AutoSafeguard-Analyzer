import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from sysml.sysml_repository import SysMLRepository


class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)

    def metrics(self, name: str) -> int:
        return 1


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y


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
    win.font = DummyFont()
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
    return win


def test_process_area_resize_clamped_to_children():
    win = _setup_window()
    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 50.0, 0.0, area=area)
    win.selected_obj = area
    win.resizing_obj = area
    win.resize_edge = "e"

    class Event:
        x = 40
        y = 0

    win.on_left_drag(Event())
    assert area.x + area.width / 2 >= wp.x + wp.width / 2


def test_process_area_resize_respects_text_size():
    win = _setup_window()
    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    area.width = 50.0
    win.selected_obj = area
    win.resizing_obj = area
    win.resize_edge = "w"

    class Event:
        x = 40
        y = 0

    win.on_left_drag(Event())
    expected_min_w = len("Risk Assessment") + 10
    assert area.width >= expected_min_w
