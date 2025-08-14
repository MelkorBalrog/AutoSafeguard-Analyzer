import types
import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sysml.sysml_repository import SysMLRepository
from gui.architecture import SysMLDiagramWindow, SysMLObject, DiagramConnection


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
    def __init__(self, x, y, state=0):
        self.x = x
        self.y = y
        self.state = state


class GovernanceConnectionDragTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def _create_window(self):
        repo = self.repo
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        win.repo = repo
        win.diagram_id = diag.diag_id
        a = SysMLObject(1, "Work Product", 0.0, 0.0)
        b = SysMLObject(2, "Work Product", 100.0, 0.0)
        win.objects = [a, b]
        conn = DiagramConnection(a.obj_id, b.obj_id, "Flow")
        win.connections = [conn]
        win.canvas = DummyCanvas()
        win.zoom = 1.0
        win.current_tool = "Select"
        win.selected_obj = None
        win.selected_objs = []
        win.selected_conn = None
        win.dragging_point_index = None
        win.dragging_endpoint = None
        win.conn_drag_offset = None
        win.endpoint_drag_pos = None
        win.start = None
        win.temp_line_end = None
        win.select_rect_start = None
        win.resizing_obj = None
        win.drag_offset = (0, 0)
        win.find_connection = lambda *args, **kwargs: conn
        win.get_object = SysMLDiagramWindow.get_object.__get__(win)
        win.redraw = lambda: None
        win._sync_to_repository = lambda: None
        win.update_property_view = lambda: None
        return win, conn

    def test_connection_midpoint_drag_creates_custom_point(self):
        win, conn = self._create_window()
        win.on_left_press(DummyEvent(50, 0))
        self.assertEqual(win.dragging_point_index, 0)
        self.assertEqual(conn.style, "Custom")
        win.on_left_drag(DummyEvent(60, 10))
        self.assertEqual(conn.points[0], (60.0, 10.0))


if __name__ == "__main__":
    unittest.main()
