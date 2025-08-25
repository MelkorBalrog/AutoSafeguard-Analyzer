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
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mainappsrc.models.sysml.sysml_repository import SysMLRepository, SysMLDiagram
from gui.architecture import SysMLDiagramWindow, DiagramConnection, SysMLObject


class DummyCanvas:
    def __init__(self):
        self.texts = []
    def create_text(self, *args, **kwargs):
        self.texts.append((args, kwargs))
    def create_line(self, *args, **kwargs):
        pass
    def create_rectangle(self, *args, **kwargs):
        pass
    def create_polygon(self, *args, **kwargs):
        pass
    def create_image(self, *args, **kwargs):
        pass
    def create_oval(self, *args, **kwargs):
        pass


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Internal Block Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.zoom = 1
        self.font = None
        self.canvas = DummyCanvas()
        self.edge_point = lambda obj, _x, _y, _r: (obj.x, obj.y)
        self.connections = []
        self.selected_objs = []
        self.selected_obj = None
        self.gradient_cache = {}
    def _label_offset(self, conn, diag_type):
        return SysMLDiagramWindow._label_offset(self, conn, diag_type)


class ConnectionLabelOffsetTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_offset_multiple_labels(self):
        win = DummyWindow()
        a = SysMLObject(1, "Existing Element", 0, 0)
        b = SysMLObject(2, "Existing Element", 100, 0)
        conn1 = DiagramConnection(1, 2, "Association")
        conn2 = DiagramConnection(1, 2, "Association")
        win.connections = [conn1, conn2]
        SysMLDiagramWindow.draw_connection(win, a, b, conn1)
        SysMLDiagramWindow.draw_connection(win, a, b, conn2)
        self.assertEqual(len(win.canvas.texts), 2)
        y0 = win.canvas.texts[0][0][1]
        y1 = win.canvas.texts[1][0][1]
        self.assertNotEqual(y0, y1)
        self.assertEqual(abs(y0 - y1), 15)

    def test_offset_vertical_labels(self):
        win = DummyWindow()
        a = SysMLObject(1, "Existing Element", 0, 0)
        b = SysMLObject(2, "Existing Element", 0, 100)
        conn1 = DiagramConnection(1, 2, "Association")
        conn2 = DiagramConnection(1, 2, "Association")
        win.connections = [conn1, conn2]
        SysMLDiagramWindow.draw_connection(win, a, b, conn1)
        SysMLDiagramWindow.draw_connection(win, a, b, conn2)
        self.assertEqual(len(win.canvas.texts), 2)
        x0 = win.canvas.texts[0][0][0]
        x1 = win.canvas.texts[1][0][0]
        self.assertNotEqual(x0, x1)
        self.assertEqual(abs(x0 - x1), 15)


if __name__ == "__main__":
    unittest.main()
