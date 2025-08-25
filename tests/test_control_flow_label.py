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
from gui.architecture import SysMLDiagramWindow, SysMLObject
from mainappsrc.models.sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyCanvas:
    def __init__(self):
        self.texts = []

    def create_text(self, *args, **kwargs):
        self.texts.append((args, kwargs))

    def create_image(self, *args, **kwargs):
        pass

    def create_rectangle(self, *args, **kwargs):
        pass

    def create_polygon(self, *args, **kwargs):
        pass

    def create_line(self, *args, **kwargs):
        pass

    def create_oval(self, *args, **kwargs):
        pass


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.zoom = 1
        self.font = None
        self.canvas = DummyCanvas()
        self.gradient_cache = {}
        self.selected_objs = []
        self.selected_obj = None
        self._draw_gradient_rect = lambda *args, **kwargs: None
        self._create_round_rect = lambda *args, **kwargs: None
        self._draw_subdiagram_marker = lambda *args, **kwargs: None


class ControlFlowLabelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_existing_element_single_label(self):
        win = DummyWindow()
        element = win.repo.create_element("Block", name="Controller")
        win.repo.add_element_to_diagram(win.diagram_id, element.elem_id)
        obj = SysMLObject(
            1,
            "Existing Element",
            10,
            20,
            width=40,
            height=20,
            element_id=element.elem_id,
            properties={"name": element.name},
        )
        SysMLDiagramWindow.draw_object(win, obj)
        self.assertEqual(len(win.canvas.texts), 1)
        args, kwargs = win.canvas.texts[0]
        self.assertEqual((args[0], args[1]), (obj.x, obj.y))
        self.assertEqual(kwargs.get("anchor"), "center")


if __name__ == "__main__":
    unittest.main()
