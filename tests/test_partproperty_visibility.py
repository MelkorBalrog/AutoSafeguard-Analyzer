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
from gui.architecture import _sync_ibd_partproperty_parts
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class PartPropertyVisibilityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_partproperty_hidden_by_default(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id)
        part = next(o for o in ibd.objects if o.get("properties", {}).get("definition") == part_blk.elem_id)
        self.assertTrue(part.get("hidden", False))
        self.assertTrue(any(d.get("hidden", False) for d in added))

    def test_partproperty_default_size(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id)
        part = added[0]
        self.assertIn("width", part)
        self.assertIn("height", part)
        self.assertGreater(part["width"], 0)
        self.assertGreater(part["height"], 0)

    def test_partproperty_visible_flag(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id, hidden=False)
        part = next(o for o in ibd.objects if o.get("properties", {}).get("definition") == part_blk.elem_id)
        self.assertFalse(part.get("hidden", True))
        self.assertTrue(any(not d.get("hidden", True) for d in added))

if __name__ == "__main__":
    unittest.main()
