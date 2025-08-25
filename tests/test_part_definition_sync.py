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

class PartDefinitionSyncTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_rename_block_updates_name_based_definition(self):
        repo = self.repo
        blk = repo.create_element("Block", name="B")
        part = repo.create_element("Part", name="B", properties={"definition": "B"})
        rename_block(repo, blk.elem_id, "B2")
        self.assertEqual(part.name, "B2")
        self.assertEqual(part.properties["definition"], blk.elem_id)

    def test_from_dict_converts_definition_names(self):
        repo = self.repo
        blk = repo.create_element("Block", name="B")
        part = repo.create_element("Part", name="B", properties={"definition": "B"})
        data = repo.to_dict()
        SysMLRepository._instance = None
        repo2 = SysMLRepository.get_instance()
        repo2.from_dict(data)
        p2 = repo2.elements[part.elem_id]
        self.assertEqual(p2.properties["definition"], blk.elem_id)

