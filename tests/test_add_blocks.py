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
from unittest.mock import patch
from gui import architecture
from gui.architecture import BlockDiagramWindow, SysMLObject
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class DummyWindow:
    _add_block_relationships = BlockDiagramWindow._add_block_relationships

    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.objects = []
        self.connections = []
        self.app = None

    def _sync_to_repository(self):
        diag = self.repo.diagrams[self.diagram_id]
        diag.objects = [obj.__dict__ for obj in self.objects]

    def redraw(self):
        pass

    def ensure_text_fits(self, obj):
        pass

class AddBlocksTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_block_from_other_diagram(self):
        repo = self.repo
        block = repo.create_element("Block", name="A")
        d1 = repo.create_diagram("Block Diagram")
        repo.add_element_to_diagram(d1.diag_id, block.elem_id)
        d1.objects.append({
            "obj_id": 1,
            "obj_type": "Block",
            "x": 0,
            "y": 0,
            "element_id": block.elem_id,
            "properties": {"name": "A"},
        })
        d2 = repo.create_diagram("Block Diagram")
        win = DummyWindow(d2)
        class DummyDialog:
            def __init__(self, parent, names, title="Select Blocks"):
                self.result = names
        with patch.object(architecture.SysMLObjectDialog, 'SelectNamesDialog', DummyDialog):
            BlockDiagramWindow.add_blocks(win)
        diag = repo.diagrams[d2.diag_id]
        self.assertEqual(len(diag.objects), 1)
        self.assertEqual(diag.objects[0].get("element_id"), block.elem_id)

if __name__ == '__main__':
    unittest.main()
