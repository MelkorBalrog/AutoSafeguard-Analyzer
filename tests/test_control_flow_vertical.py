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

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id

class ControlFlowConnectionTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_vertical_connection_valid(self):
        win = DummyWindow()
        src = SysMLObject(1, "Existing Element", 0, 0)
        dst = SysMLObject(2, "Existing Element", 1, 100)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Control Action")
        self.assertTrue(valid)

    def test_connection_too_offset_invalid(self):
        win = DummyWindow()
        src = SysMLObject(1, "Existing Element", 0, 0)
        dst = SysMLObject(2, "Existing Element", 200, 100)
        valid, msg = SysMLDiagramWindow.validate_connection(win, src, dst, "Control Action")
        self.assertFalse(valid)
        self.assertEqual(msg, "Connections must be vertical")

if __name__ == "__main__":
    unittest.main()
