import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject

class EdgePointTests(unittest.TestCase):
    def setUp(self):
        self.win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        self.win.zoom = 1.0

    def test_diagonal_to_square_corner(self):
        obj = SysMLObject(1, "Action", 0, 0, width=20, height=20)
        x, y = self.win.edge_point(obj, 20, 20)
        self.assertAlmostEqual(x, 10.0)
        self.assertAlmostEqual(y, 10.0)

if __name__ == "__main__":
    unittest.main()
