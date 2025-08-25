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

from gui.drawing_helper import GSNDrawingHelper


class DummyCanvas:
    """Minimal canvas stub capturing drawn lines."""

    def __init__(self):
        self.lines = []

    def create_line(self, x1, y1, x2, y2, fill=None):  # pragma: no cover - simple storage
        self.lines.append(fill)


def test_fill_gradient_rect_accepts_named_color():
    helper = GSNDrawingHelper()
    canvas = DummyCanvas()
    # Using a Tk-style color name previously triggered a ValueError
    helper._fill_gradient_rect(canvas, 0, 0, 4, 4, "lightyellow")
    assert canvas.lines  # some lines were drawn
    assert all(line.startswith("#") for line in canvas.lines)

