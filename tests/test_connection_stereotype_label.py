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
from gui.architecture import DiagramConnection, format_control_flow_label
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class ConnectionStereotypeLabelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_association_label_stereotype(self):
        conn = DiagramConnection(1, 2, "Association")
        label = format_control_flow_label(conn, self.repo, None)
        self.assertEqual(label, "<<association>>")

    def test_association_label_with_name(self):
        conn = DiagramConnection(1, 2, "Association", name="rel")
        label = format_control_flow_label(conn, self.repo, None)
        self.assertEqual(label, "<<association>> rel")

    def test_propagate_label_stereotype(self):
        conn = DiagramConnection(1, 2, "Propagate")
        label = format_control_flow_label(conn, self.repo, "Governance Diagram")
        self.assertEqual(label, "<<propagate>>")

    def test_governance_relationship_guard_label(self):
        conn = DiagramConnection(1, 2, "Trace", guard=["g1"])
        label = format_control_flow_label(conn, self.repo, "Governance Diagram")
        self.assertEqual(label, "[g1] / <<trace>>")


if __name__ == "__main__":
    unittest.main()
