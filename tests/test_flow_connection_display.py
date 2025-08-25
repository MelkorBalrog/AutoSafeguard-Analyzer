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
from gui.architecture import DiagramConnection, _arrow_forward_types, format_control_flow_label
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class FlowConnectionDisplayTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_flow_arrow_and_label(self):
        arrow_default = "forward" if "Flow" in _arrow_forward_types() else "none"
        conn = DiagramConnection(1, 2, "Flow", name="<<flow>>", arrow=arrow_default)
        label = format_control_flow_label(conn, self.repo, "Governance Diagram")
        self.assertEqual(label, "<<flow>>")
        self.assertEqual(conn.arrow, "forward")


if __name__ == "__main__":
    unittest.main()
