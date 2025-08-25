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
from gui.architecture import (
    add_aggregation_part,
    add_composite_aggregation_part,
    remove_aggregation_part,
)
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class GeneralizationPartUpdateTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_aggregation_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="PartA")
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertIn(
            "PartA",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_add_composite_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="PartB")
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertIn(
            "PartB",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_remove_aggregation_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="PartC")
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertIn(
            "PartC",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )
        remove_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertNotIn(
            "PartC",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_multiplicity_change_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="P")
        child = repo.create_element("Block", name="C")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="B")
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id, "1")
        self.assertEqual(
            repo.elements[child.elem_id].properties.get("partProperties"),
            "B[1]",
        )
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id, "3")
        self.assertEqual(
            repo.elements[child.elem_id].properties.get("partProperties"),
            "B[3]",
        )


if __name__ == "__main__":
    unittest.main()
