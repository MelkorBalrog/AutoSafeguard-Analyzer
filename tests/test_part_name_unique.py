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
from gui import architecture
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class PartNameUniqueTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_detect_duplicate_name_across_diagrams(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)
        ibd_a = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd_a.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id)
        obj = next(o for o in ibd_a.objects if o.get("obj_type") == "Part")
        repo.elements[obj["element_id"]].name = "P"

        ibd_b = repo.create_diagram("Internal Block Diagram")
        boundary = {
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 0,
            "y": 0,
            "width": 80.0,
            "height": 40.0,
            "element_id": a.elem_id,
            "properties": {},
        }
        ibd_b.objects.append(boundary)

        exists = architecture._part_name_exists(repo, a.elem_id, "P")
        self.assertTrue(exists)


if __name__ == "__main__":
    unittest.main()

