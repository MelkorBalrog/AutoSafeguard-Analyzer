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
    _sync_ibd_partproperty_parts,
    propagate_block_changes,
    remove_partproperty_entry,
)
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class RemovePartPropertyTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_remove_partproperty_updates_child_ibds(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        ibd_p = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(parent.elem_id, ibd_p.diag_id)
        ibd_c = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd_c.diag_id)

        _sync_ibd_partproperty_parts(repo, parent.elem_id)
        propagate_block_changes(repo, parent.elem_id)

        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd_c.objects
            )
        )

        remove_partproperty_entry(repo, parent.elem_id, "B")

        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd_c.objects
            )
        )

if __name__ == "__main__":
    unittest.main()
