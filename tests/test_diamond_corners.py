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
