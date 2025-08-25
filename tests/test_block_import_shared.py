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

from gui.architecture import rename_block
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class BlockImportSharedTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_imported_block_shares_element(self):
        repo = self.repo
        d1 = repo.create_diagram("Block Diagram")
        d2 = repo.create_diagram("Block Diagram")
        blk = repo.create_element("Block", name="A", properties={"ports": "p1"})

        repo.add_element_to_diagram(d1.diag_id, blk.elem_id)
        d1.objects = [
            {
                "obj_id": 1,
                "obj_type": "Block",
                "x": 0,
                "y": 0,
                "element_id": blk.elem_id,
                "properties": {"name": blk.name, **blk.properties},
            }
        ]

        repo.add_element_to_diagram(d2.diag_id, blk.elem_id)
        d2.objects = [
            {
                "obj_id": 2,
                "obj_type": "Block",
                "x": 0,
                "y": 0,
                "element_id": blk.elem_id,
                "properties": {"name": blk.name, **blk.properties},
            }
        ]

        d1.objects.clear()
        d1.elements.remove(blk.elem_id)

        rename_block(repo, blk.elem_id, "B")

        self.assertEqual(repo.elements[blk.elem_id].name, "B")
        self.assertEqual(d2.objects[0]["properties"]["name"], "B")
        self.assertEqual(d2.objects[0]["properties"]["ports"], "p1")


if __name__ == "__main__":
    unittest.main()
