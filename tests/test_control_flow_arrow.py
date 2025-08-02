import unittest
import tkinter as tk
from gui.architecture import SysMLDiagramWindow, SysMLObject, DiagramConnection
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyCanvas:
    def __init__(self):
        self.last_line = None
    def create_line(self, *args, **kwargs):
        self.last_line = (args, kwargs)
    def create_text(self, *args, **kwargs):
        pass


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.zoom = 1
        self.font = None
        self.canvas = DummyCanvas()
        self.edge_point = lambda obj, _x, _y, _r: (obj.x, obj.y)
        self.connections = []
        self.objects = []


def reset_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


class ControlFlowArrowTests(unittest.TestCase):
    def setUp(self):
        reset_repo()

    def test_arrow_up(self):
        win = DummyWindow()
        a = SysMLObject(1, "Existing Element", 0, 100)
        b = SysMLObject(2, "Existing Element", 0, 0)
        conn = DiagramConnection(1, 2, "Control Action")
        SysMLDiagramWindow.draw_connection(win, a, b, conn)
        args, kwargs = win.canvas.last_line
        self.assertEqual(kwargs.get("arrow"), tk.LAST)
        x1, y1, x2, y2 = args
        self.assertEqual(x1, x2)
        self.assertGreater(y1, y2)

    def test_arrow_up_offset(self):
        win = DummyWindow()
        a = SysMLObject(1, "Existing Element", 0, 100)
        b = SysMLObject(2, "Existing Element", 80, 0)
        conn = DiagramConnection(1, 2, "Control Action")
        SysMLDiagramWindow.draw_connection(win, a, b, conn)
        args, kwargs = win.canvas.last_line
        self.assertEqual(kwargs.get("arrow"), tk.LAST)
        x1, y1, x2, y2 = args
        self.assertEqual(x1, x2)
        self.assertEqual(x1, 40)
        self.assertGreater(y1, y2)

    def test_validate_connection_limits_offset(self):
        win = DummyWindow()
        a = SysMLObject(1, "Existing Element", 0, 0)
        b = SysMLObject(2, "Existing Element", 80, 100)
        valid, _ = SysMLDiagramWindow.validate_connection(win, a, b, "Control Action")
        self.assertTrue(valid)
        b2 = SysMLObject(3, "Existing Element", 81, 100)
        valid, msg = SysMLDiagramWindow.validate_connection(win, a, b2, "Control Action")
        self.assertFalse(valid)
        self.assertEqual(msg, "Connections must be vertical")

    def test_constrain_horizontal_movement(self):
        win = DummyWindow()
        a = SysMLObject(1, "Existing Element", 0, 100)
        b = SysMLObject(2, "Existing Element", 0, 0)
        win.objects = [a, b]
        conn = DiagramConnection(1, 2, "Control Action")
        win.connections = [conn]
        new_x = SysMLDiagramWindow._constrain_horizontal_movement(win, a, 200)
        self.assertEqual(new_x, 80)


if __name__ == "__main__":
    unittest.main()
