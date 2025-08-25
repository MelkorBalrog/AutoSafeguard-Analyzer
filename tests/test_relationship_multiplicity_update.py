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

class RelationMultiplicityUpdateTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_update_relationship_multiplicity(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        rel = repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id, "2")
        self.assertEqual(rel.properties.get("multiplicity"), "2")
