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

import pytest
from gui.architecture import SysMLDiagramWindow, SysMLObject

class DummyWindow:
    def __init__(self):
        self.zoom = 1.0

@pytest.mark.parametrize(
    "tx, ty, expected",
    [
        (10, 0, (6, 0)),   # right side
        (-10, 0, (-6, 0)), # left side
        (0, 10, (0, 6)),   # bottom side (positive y)
        (0, -10, (0, -6)), # top side
    ],
)
def test_edge_point_on_port(tx, ty, expected):
    win = DummyWindow()
    port = SysMLObject(1, "Port", 0, 0)
    x, y = SysMLDiagramWindow.edge_point(win, port, tx, ty)
    assert abs(x - expected[0]) < 1e-6
    assert abs(y - expected[1]) < 1e-6
