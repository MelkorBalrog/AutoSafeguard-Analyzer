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
    propagate_block_port_changes,
    propagate_block_changes,
    parse_operations,
)
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class BlockChangePropagationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_block_change_propagates_to_children(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)

        ibd_parent = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(parent.elem_id, ibd_parent.diag_id)
        ibd_child = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd_child.diag_id)

        ibd_parent.objects.append({
            "obj_id": 1,
            "obj_type": "Block",
            "x": 0,
            "y": 0,
            "element_id": parent.elem_id,
            "properties": {},
            "requirements": [{"id": "R1"}],
        })
        ibd_child.objects.append({
            "obj_id": 2,
            "obj_type": "Block",
            "x": 0,
            "y": 0,
            "element_id": child.elem_id,
            "properties": {},
            "requirements": [],
        })

        parent.properties["operations"] = '[{"name":"opA"}]'
        parent.properties["ports"] = "p1"
        part = repo.create_element("Block", name="Part")
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        propagate_block_port_changes(repo, parent.elem_id)

        propagate_block_changes(repo, parent.elem_id)

        ops = parse_operations(child.properties.get("operations", ""))
        self.assertTrue(any(o.name == "opA" for o in ops))
        self.assertIn("p1", child.properties.get("ports", ""))
        self.assertIn("Part", child.properties.get("partProperties", ""))
        self.assertEqual(ibd_child.objects[0]["requirements"][0]["id"], "R1")


if __name__ == "__main__":
    unittest.main()
