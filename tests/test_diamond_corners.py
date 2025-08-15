import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow

class DummyWindow:
    def __init__(self):
        self.zoom = 1.0

    _nearest_diamond_corner = SysMLDiagramWindow._nearest_diamond_corner
    _segment_intersection = SysMLDiagramWindow._segment_intersection
    edge_point = SysMLDiagramWindow.edge_point
    _segment_intersection = SysMLDiagramWindow._segment_intersection

class DiamondCornerTests(unittest.TestCase):
    def test_edge_point_nearest_corner(self):
        win = DummyWindow()
        obj = SysMLObject(1, "Decision", 0, 0, width=40.0, height=40.0)
        self.assertEqual(win.edge_point(obj, 100.0, 0.0), (20.0, 0.0))
        self.assertEqual(win.edge_point(obj, -100.0, 0.0), (-20.0, 0.0))
        self.assertEqual(win.edge_point(obj, 0.0, -100.0), (0.0, -20.0))
        self.assertEqual(win.edge_point(obj, 0.0, 100.0), (0.0, 20.0))

if __name__ == "__main__":
    unittest.main()
