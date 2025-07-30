import unittest
from gui.architecture import SysMLObject, _boundary_min_size, ensure_boundary_contains_parts

class BoundarySizeTests(unittest.TestCase):
    def test_min_size_computes_extent(self):
        boundary = SysMLObject(1, "Block Boundary", 0.0, 0.0, width=10.0, height=10.0)
        part = SysMLObject(2, "Part", 30.0, 0.0, width=10.0, height=10.0)
        w, h = _boundary_min_size(boundary, [boundary, part])
        self.assertEqual(w, 90.0)
        self.assertEqual(h, 30.0)

    def test_ensure_boundary_expands(self):
        boundary = SysMLObject(1, "Block Boundary", 0.0, 0.0, width=50.0, height=50.0)
        part = SysMLObject(2, "Part", 40.0, 0.0, width=20.0, height=20.0)
        ensure_boundary_contains_parts(boundary, [boundary, part])
        w, h = _boundary_min_size(boundary, [boundary, part])
        self.assertEqual(boundary.width, w)
        self.assertEqual(boundary.height, 50.0)

if __name__ == "__main__":
    unittest.main()
