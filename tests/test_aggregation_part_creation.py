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
    _sync_ibd_aggregation_parts,
    propagate_block_part_changes,
    remove_aggregation_part,
)
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class AggregationPartCreationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_aggregation_creates_part(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Aggregation", whole.elem_id, part.elem_id)
        add_aggregation_part(repo, whole.elem_id, part.elem_id)
        rel = next(
            r
            for r in repo.relationships
            if r.rel_type == "Aggregation"
            and r.source == whole.elem_id
            and r.target == part.elem_id
        )
        pid = rel.properties.get("part_elem")
        self.assertIsNotNone(pid)
        self.assertIn(pid, repo.elements)
        self.assertEqual(repo.elements[pid].properties.get("definition"), part.elem_id)

    def test_part_updates_with_block(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Aggregation", whole.elem_id, part.elem_id)
        add_aggregation_part(repo, whole.elem_id, part.elem_id)
        rel = next(
            r
            for r in repo.relationships
            if r.rel_type == "Aggregation"
            and r.source == whole.elem_id
            and r.target == part.elem_id
        )
        pid = rel.properties.get("part_elem")
        part.properties["operations"] = '[{"name":"op"}]'
        propagate_block_part_changes(repo, part.elem_id)
        self.assertEqual(repo.elements[pid].properties.get("operations"), part.properties["operations"])

    def test_part_name_sync_on_block_rename(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Aggregation", whole.elem_id, part.elem_id)
        add_aggregation_part(repo, whole.elem_id, part.elem_id)
        rel = next(
            r
            for r in repo.relationships
            if r.rel_type == "Aggregation"
            and r.source == whole.elem_id
            and r.target == part.elem_id
        )
        pid = rel.properties.get("part_elem")
        part.name = "Renamed"
        propagate_block_part_changes(repo, part.elem_id)
        self.assertTrue(repo.elements[pid].name.startswith("Renamed"))

    def test_remove_aggregation_part_object(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Aggregation", whole.elem_id, part.elem_id)
        add_aggregation_part(repo, whole.elem_id, part.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        _sync_ibd_aggregation_parts(repo, whole.elem_id)
        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd.objects
            )
        )
        remove_aggregation_part(repo, whole.elem_id, part.elem_id, remove_object=True)
        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd.objects
            )
        )
        rel = next(
            r
            for r in repo.relationships
            if r.rel_type == "Aggregation"
            and r.source == whole.elem_id
            and r.target == part.elem_id
        )
        self.assertNotIn(rel.properties.get("part_elem"), repo.elements)


if __name__ == "__main__":
    unittest.main()
