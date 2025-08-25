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
from gui.architecture import _sync_block_parts_from_ibd
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class IBDPartBlockUpdateTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_part_definition_adds_block_part(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part_blk = repo.create_element("Block", name="Inner")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        part_elem = repo.create_element(
            "Part", name="Inner", properties={"definition": part_blk.elem_id}
        )
        ibd.objects.append(
            {
                "obj_id": 1,
                "obj_type": "Part",
                "x": 0,
                "y": 0,
                "element_id": part_elem.elem_id,
                "properties": {"definition": part_blk.elem_id},
            }
        )
        _sync_block_parts_from_ibd(repo, ibd.diag_id)
        self.assertIn(
            "Inner",
            repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )

if __name__ == "__main__":
    unittest.main()
