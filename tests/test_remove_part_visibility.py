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
from mainappsrc.models.sysml.sysml_repository import SysMLRepository, SysMLDiagram

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Internal Block Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.objects = []
        self.connections = []
        self.selected_obj = None

    def _sync_to_repository(self):
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [obj.__dict__ for obj in self.objects]
            diag.connections = [conn.__dict__ for conn in self.connections]

    def redraw(self):
        pass

    def update_property_view(self):
        pass

class RemovePartVisibilityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_remove_part_diagram_marks_hidden(self):
        win = DummyWindow()
        part = SysMLObject(1, "Part", 0, 0)
        win.objects = [part]
        SysMLDiagramWindow.remove_part_diagram(win, part)
        self.assertIn(part, win.objects)
        self.assertTrue(part.hidden)

if __name__ == "__main__":
    unittest.main()
