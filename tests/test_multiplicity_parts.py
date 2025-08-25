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
from gui.architecture import add_composite_aggregation_part, add_multiplicity_parts
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class MultiplicityPartTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_exact_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "3")
        objs = [
            o for o in ibd.objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 3)
        names = {repo.elements[o["element_id"]].name for o in objs}
        self.assertIn("Part[1]", names)
        self.assertIn("Part[3]", names)

    def test_unbounded_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="W")
        part = repo.create_element("Block", name="P")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "1..*")
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..*", count=3)
        objs = [
            o for o in ibd.objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 4)

    def test_update_existing_parts(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="P")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "1")
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "3")
        names = [
            repo.elements[o["element_id"]].name
            for o in ibd.objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(names, ["P[1]", "P[2]", "P[3]"])
\
    def test_multiplicity_decrease_removes_parts(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "3")
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "1")
        objs = [
            o
            for o in ibd.objects
            if o.get("obj_type") == "Part"
            and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 1)
        self.assertEqual(repo.elements[objs[0]["element_id"]].name, "Part[1]")

    def test_add_parts_up_to_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "1..3")
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..3", count=1)
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..3", count=1)
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..3", count=1)
        objs = [
            o
            for o in ibd.objects
            if o.get("obj_type") == "Part"
            and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 3)

    def test_multiplicity_decrease_removes_parts(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "3")
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "1")
        objs = [
            o
            for o in ibd.objects
            if o.get("obj_type") == "Part"
            and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 1)
        self.assertEqual(repo.elements[objs[0]["element_id"]].name, "Part[1]")

    def test_add_parts_up_to_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "1..3")
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..3", count=1)
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..3", count=1)
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..3", count=1)
        objs = [
            o
            for o in ibd.objects
            if o.get("obj_type") == "Part"
            and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 3)

    def test_single_multiplicity_limit(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1", count=1)
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1", count=1)
        objs = [
            o
            for o in ibd.objects
            if o.get("obj_type") == "Part"
            and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 1)

if __name__ == "__main__":
    unittest.main()
