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
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from analysis.user_config import set_current_user
from gui.architecture import rename_block, add_aggregation_part

class UndoTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        set_current_user("Tester", "tester@example.com")
        self.repo = SysMLRepository.get_instance()

    def test_undo_creation(self):
        elem = self.repo.create_element("Actor", name="User")
        self.assertIn(elem.elem_id, self.repo.elements)
        self.assertTrue(self.repo.undo())
        self.assertNotIn(elem.elem_id, self.repo.elements)

    def test_undo_rename_block(self):
        blk = self.repo.create_element("Block", name="A")
        rename_block(self.repo, blk.elem_id, "B")
        self.assertEqual(self.repo.elements[blk.elem_id].name, "B")
        self.assertTrue(self.repo.undo())
        self.assertEqual(self.repo.elements[blk.elem_id].name, "A")

    def test_undo_add_aggregation(self):
        whole = self.repo.create_element("Block", name="Whole")
        part = self.repo.create_element("Block", name="Part")
        add_aggregation_part(self.repo, whole.elem_id, part.elem_id)
        self.assertIn(
            "Part",
            self.repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )
        self.assertTrue(self.repo.undo())
        self.assertNotIn(
            "Part",
            self.repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )

    def test_redo_creation(self):
        elem = self.repo.create_element("Actor", name="User")
        self.repo.undo()
        self.assertNotIn(elem.elem_id, self.repo.elements)
        self.assertTrue(self.repo.redo())
        self.assertIn(elem.elem_id, self.repo.elements)

    def test_redo_rename_block(self):
        blk = self.repo.create_element("Block", name="A")
        rename_block(self.repo, blk.elem_id, "B")
        self.repo.undo()
        self.assertEqual(self.repo.elements[blk.elem_id].name, "A")
        self.assertTrue(self.repo.redo())
        self.assertEqual(self.repo.elements[blk.elem_id].name, "B")

    def test_undo_redo_relationship(self):
        src = self.repo.create_element("Block", name="Src")
        tgt = self.repo.create_element("Block", name="Tgt")
        rel = self.repo.create_relationship("Association", src.elem_id, tgt.elem_id)
        self.assertIn(rel, self.repo.relationships)
        self.assertTrue(self.repo.undo())
        self.assertNotIn(rel, self.repo.relationships)
        self.assertTrue(self.repo.redo())
        self.assertIn(rel, self.repo.relationships)

    def test_undo_redo_link_diagram(self):
        elem = self.repo.create_element("Block", name="A")
        diag = self.repo.create_diagram("ibd", name="D")
        self.repo.link_diagram(elem.elem_id, diag.diag_id)
        self.assertEqual(self.repo.get_linked_diagram(elem.elem_id), diag.diag_id)
        self.assertTrue(self.repo.undo())
        self.assertIsNone(self.repo.get_linked_diagram(elem.elem_id))
        self.assertTrue(self.repo.redo())
        self.assertEqual(self.repo.get_linked_diagram(elem.elem_id), diag.diag_id)

if __name__ == '__main__':
    unittest.main()
