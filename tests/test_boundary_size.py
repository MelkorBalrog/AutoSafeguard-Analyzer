# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from gui.architecture import SysMLObject, _boundary_min_size, ensure_boundary_contains_parts

class BoundarySizeTests(unittest.TestCase):
    def test_min_size_computes_extent(self):
        boundary = SysMLObject(1, "Block Boundary", 0.0, 0.0, width=10.0, height=10.0)
        part = SysMLObject(2, "Part", 30.0, 0.0, width=10.0, height=10.0)
        w, h = _boundary_min_size(boundary, [boundary, part])
        self.assertEqual(w, 30.0)
        self.assertEqual(h, 30.0)

    def test_ensure_boundary_expands(self):
        boundary = SysMLObject(1, "Block Boundary", 0.0, 0.0, width=50.0, height=50.0)
        part = SysMLObject(2, "Part", 40.0, 0.0, width=20.0, height=20.0)
        ensure_boundary_contains_parts(boundary, [boundary, part])
        w, h = _boundary_min_size(boundary, [boundary, part])
        self.assertGreaterEqual(boundary.width, w)
        self.assertGreaterEqual(boundary.height, h)

if __name__ == "__main__":
    unittest.main()
