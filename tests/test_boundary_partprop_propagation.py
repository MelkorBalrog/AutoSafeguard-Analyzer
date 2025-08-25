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
from gui.architecture import _sync_ibd_partproperty_parts, _propagate_boundary_parts
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class BoundaryPartPropagationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_new_parts_show_in_boundary_diagrams(self):
        repo = self.repo
        block_a = repo.create_element("Block", name="A")
        block_b = repo.create_element("Block", name="B")
        block_c = repo.create_element("Block", name="C")
        ibd_b = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block_b.elem_id, ibd_b.diag_id)
        ibd_a = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block_a.elem_id, ibd_a.diag_id)
        ibd_a.objects.append({
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 100.0,
            "y": 80.0,
            "width": 200.0,
            "height": 120.0,
            "element_id": block_b.elem_id,
            "properties": {"name": "B"},
        })
        block_b.properties["partProperties"] = "C"
        added = _sync_ibd_partproperty_parts(repo, block_b.elem_id, visible=True)
        _propagate_boundary_parts(repo, block_b.elem_id, added)
        self.assertTrue(any(
            o.get("obj_type") == "Part" and o.get("element_id") == added[0]["element_id"]
            for o in ibd_a.objects
        ))
        part = next(o for o in ibd_a.objects if o.get("element_id") == added[0]["element_id"])
        self.assertFalse(part.get("hidden", False))

if __name__ == "__main__":
    unittest.main()
