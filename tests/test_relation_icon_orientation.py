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

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import gui.icon_factory as icons


def test_relation_icon_arrowhead_shape(monkeypatch):
    class DummyImage:
        def __init__(self, *args, **kwargs):
            self.coords = set()
        def put(self, color, pos=None, to=None):
            if pos is not None:
                self.coords.add(pos)
            else:
                x1, y1, x2, y2 = to
                for x in range(x1, x2):
                    for y in range(y1, y2):
                        self.coords.add((x, y))
    monkeypatch.setattr(icons.tk, "PhotoImage", DummyImage)
    img = icons.create_icon("relation", "black")
    mid = 16 // 2
    left_head = {(i, mid - i) for i in range(4)} | {(i, mid + i) for i in range(4)}
    inverted_head = {(3 - i, mid - i) for i in range(4)} | {(3 - i, mid + i) for i in range(4)}
    right_head = {(16 - 4 + i, mid - i) for i in range(1, 4)} | {(16 - 4 + i, mid + i) for i in range(1, 4)}
    assert left_head <= img.coords
    assert not any(pt in img.coords for pt in inverted_head | right_head)
