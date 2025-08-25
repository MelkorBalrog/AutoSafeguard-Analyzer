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

import tkinter as tk
import types
import pytest

from gui.architecture import SysMLDiagramWindow, SysMLObject, _all_connection_tools


@pytest.mark.parametrize("tool", _all_connection_tools())
def test_temp_connection_line_is_dotted_and_animated(tool):
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.zoom = 1.0
    win.start = SysMLObject(1, "Block", 10, 20)
    win.temp_line_end = (50, 60)
    win.current_tool = tool
    win.selected_conn = None
    win.dragging_endpoint = None
    win.endpoint_drag_pos = None
    win.connections = []
    win.objects = []
    win.compartment_buttons = []
    win.gradient_cache = {}

    def edge_point(self, obj, tx, ty, rel=None, apply_radius=True):
        return obj.x * self.zoom, obj.y * self.zoom

    win.edge_point = types.MethodType(edge_point, win)

    class CanvasStub:
        def __init__(self):
            self.lines = []
            self.after_calls = 0
            self.last_dashoffset = None

        def configure(self, **kwargs):
            pass

        def delete(self, *args):
            pass

        def create_line(self, *args, **kwargs):
            self.lines.append(kwargs)
            return 1

        def tag_raise(self, *args):
            pass

        def config(self, **kwargs):
            pass

        def bbox(self, *args):
            return (0, 0, 0, 0)

        def find_withtag(self, tag):
            return [1] if tag == "_temp_conn" and self.lines else []

        def itemconfigure(self, *args, **kwargs):
            self.last_dashoffset = kwargs.get("dashoffset")

        def after(self, delay, func):
            self.after_calls += 1
            return "after_id"

        def after_cancel(self, _):
            pass

    win.canvas = CanvasStub()
    win.redraw()

    assert win.canvas.lines
    line_kwargs = win.canvas.lines[0]
    assert line_kwargs.get("dash") == (2, 2)
    assert line_kwargs.get("arrow") == tk.LAST
    assert win.canvas.after_calls == 1
    assert win.canvas.last_dashoffset == 2
