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
from gui.architecture import SysMLObject
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class MultiplicityAcrossBoundaryTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_limit_counts_parts_in_all_diagrams(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship(
            "Composite Aggregation",
            a.elem_id,
            b.elem_id,
            properties={"multiplicity": "1"},
        )
        ibd_a = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd_a.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id, "1")

        ibd_b = repo.create_diagram("Internal Block Diagram")
        boundary = {
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 0,
            "y": 0,
            "width": 100.0,
            "height": 80.0,
            "element_id": a.elem_id,
            "properties": {},
        }
        ibd_b.objects.append(boundary)

        new_elem = repo.create_element("Part", name="X")
        repo.add_element_to_diagram(ibd_b.diag_id, new_elem.elem_id)
        obj = {
            "obj_id": 2,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": new_elem.elem_id,
            "properties": {"definition": b.elem_id},
        }

        exceeded = architecture._multiplicity_limit_exceeded(
            repo,
            a.elem_id,
            b.elem_id,
            [obj],
            new_elem.elem_id,
        )
        self.assertTrue(exceeded)


if __name__ == "__main__":
    unittest.main()

