import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject, DiagramConnection
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.zoom = 1.0
        self.objects = [
            SysMLObject(1, "Existing Element", 0, 0),
            SysMLObject(2, "Existing Element", 60, 100),
        ]
        self.connections = [DiagramConnection(1, 2, "Control Action")]

    def get_object(self, oid):
        return next((o for o in self.objects if o.obj_id == oid), None)

    def edge_point(self, obj, tx, ty, rel, apply_radius=True):
        return SysMLDiagramWindow.edge_point(self, obj, tx, ty, rel, apply_radius)

    def _dist_to_segment(self, p, a, b):
        return SysMLDiagramWindow._dist_to_segment(self, p, a, b)

class ControlFlowSelectTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()

    def test_vertical_connection_selectable(self):
        win = DummyWindow()
        conn = SysMLDiagramWindow.find_connection(win, 30, 50)
        self.assertIs(conn, win.connections[0])

if __name__ == "__main__":
    unittest.main()
