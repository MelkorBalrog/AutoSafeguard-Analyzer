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
from gui.architecture import link_block_to_ibd, _ensure_ibd_boundary
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class PartPropertyNewIBDTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_parts_visible_when_ibd_created_later(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        link_block_to_ibd(repo, blk.elem_id, ibd.diag_id)
        self.assertTrue(any(
            o.get("obj_type") == "Part" and repo.elements[o.get("element_id")].name.startswith("B")
            for o in ibd.objects
        ))
        part = next(o for o in ibd.objects if repo.elements[o.get("element_id")].name.startswith("B"))
        self.assertFalse(part.get("hidden", False))

    def test_boundary_receives_parts_on_creation(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child", properties={"partProperties": "P"})
        repo.create_element("Block", name="P")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(parent.elem_id, ibd.diag_id)
        ibd.objects.append({
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 50.0,
            "y": 50.0,
            "width": 200.0,
            "height": 120.0,
            "element_id": child.elem_id,
            "properties": {"name": "Child"},
        })
        _ensure_ibd_boundary(repo, ibd, child.elem_id)
        self.assertTrue(any(
            o.get("obj_type") == "Part" and repo.elements[o.get("element_id")].name.startswith("P")
            for o in ibd.objects
        ))

if __name__ == "__main__":
    unittest.main()
