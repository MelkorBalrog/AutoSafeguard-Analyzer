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

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gui.threat_dialog import ThreatDialog
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class ThreatAssetTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_connections_and_flows_included(self):
        repo = self.repo
        # Create element to serve as connection's element with name
        elem = repo.create_element("Block", name="ConnElem")
        # Create diagram and attach a connection with element_id and flow
        diag = repo.create_diagram("Block Definition", name="BD")
        diag.connections = [
            {
                "src": 1,
                "dst": 2,
                "conn_type": "Connector",
                "element_id": elem.elem_id,
                "flow": "DataFlow",
            }
        ]
        # Call _get_assets without constructing full dialog
        dlg = ThreatDialog.__new__(ThreatDialog)
        assets = dlg._get_assets(diag.diag_id)
        self.assertIn("ConnElem", assets)
        self.assertIn("DataFlow", assets)


if __name__ == "__main__":
    unittest.main()
