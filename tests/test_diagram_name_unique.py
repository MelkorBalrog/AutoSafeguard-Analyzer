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
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class DiagramNameUniqueTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_names_include_type_when_conflict(self):
        repo = self.repo
        bdd = repo.create_diagram("Block Definition Diagram", name="Main")
        ibd = repo.create_diagram("Internal Block Diagram", name="Main")
        self.assertIn(bdd.diag_type, bdd.name)
        self.assertIn(ibd.diag_type, ibd.name)
        self.assertNotEqual(bdd.name, ibd.name)

    def test_repeated_name_does_not_duplicate(self):
        repo = self.repo
        repo.create_diagram("Block Definition Diagram", name="Main")
        repo.create_diagram("Internal Block Diagram", name="Main")
        third = repo.create_diagram("Internal Block Diagram", name="Main")
        fourth = repo.create_diagram("Block Definition Diagram", name="Main")
        names = [d.name for d in repo.diagrams.values()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(third.name, "Main Internal Block Diagram_1")
        self.assertEqual(fourth.name, "Main Block Definition Diagram_1")


if __name__ == "__main__":
    unittest.main()
