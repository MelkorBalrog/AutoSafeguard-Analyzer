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


if __name__ == "__main__":
    unittest.main()
