import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow, DiagramConnection

class DummyWindow:
    def __init__(self):
        self.zoom = 1.0
        self.connections = []

    _nearest_diamond_corner = SysMLDiagramWindow._nearest_diamond_corner
    _segment_intersection = SysMLDiagramWindow._segment_intersection
    edge_point = SysMLDiagramWindow.edge_point
    _allocate_diamond_corner = SysMLDiagramWindow._allocate_diamond_corner

class DiamondCornerTests(unittest.TestCase):
    def test_edge_point_nearest_corner(self):
        win = DummyWindow()
        obj = SysMLObject(1, "Decision", 0, 0, width=40.0, height=40.0)
        self.assertEqual(win.edge_point(obj, 100.0, 0.0), (20.0, 0.0))
        self.assertEqual(win.edge_point(obj, -100.0, 0.0), (-20.0, 0.0))
        self.assertEqual(win.edge_point(obj, 0.0, -100.0), (0.0, -20.0))
        self.assertEqual(win.edge_point(obj, 0.0, 100.0), (0.0, 20.0))

    def test_unique_corner_assignment(self):
        win = DummyWindow()
        obj = SysMLObject(1, "Decision", 0, 0, width=40.0, height=40.0)
        targets = [(100.0, 0.0), (100.0, 0.0), (100.0, 0.0), (100.0, 0.0)]
        for i, (tx, ty) in enumerate(targets, start=2):
            conn = DiagramConnection(obj.obj_id, i, "Control Flow")
            conn.src_pos = win._allocate_diamond_corner(obj, tx, ty, conn)
            win.connections.append(conn)
        positions = {c.src_pos for c in win.connections}
        self.assertEqual(len(positions), 4)

if __name__ == "__main__":
    unittest.main()
