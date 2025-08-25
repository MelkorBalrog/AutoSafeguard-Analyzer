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
import types, sys
sys.modules.setdefault('PIL', types.ModuleType('PIL'))
sys.modules.setdefault('PIL.Image', types.ModuleType('PIL.Image'))
sys.modules.setdefault('PIL.ImageDraw', types.ModuleType('PIL.ImageDraw'))
sys.modules.setdefault('PIL.ImageFont', types.ModuleType('PIL.ImageFont'))
sys.modules.setdefault('PIL.ImageTk', types.ModuleType('PIL.ImageTk'))
from AutoML import FaultTreeNode, AutoMLApp, GATE_NODE_TYPES
from analysis.models import MissionProfile, ReliabilityComponent

class DummyApp:
    def __init__(self, fm_node):
        self.mission_profiles = [MissionProfile("MP", 1.0, 0.0)]
        self.reliability_components = [ReliabilityComponent("C1", "type", quantity=4)]
        self.node_map = {fm_node.unique_id: fm_node}

    def find_node_by_id_all(self, uid):
        return self.node_map.get(uid)

    def get_failure_mode_node(self, node):
        ref = getattr(node, "failure_mode_ref", None)
        if ref:
            return self.find_node_by_id_all(ref)
        return node

    def get_component_name_for_node(self, node):
        src = self.get_failure_mode_node(node)
        parent = src.parents[0] if src.parents else None
        if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES:
            if getattr(parent, "user_name", ""):
                return parent.user_name
        return getattr(src, "fmea_component", "")

    def get_fit_for_fault(self, _):
        return 0.0

class FailureProbabilityTests(unittest.TestCase):
    def test_fit_divided_by_quantity(self):
        fm = FaultTreeNode("FM", "Basic Event")
        fm.fmea_component = "C1"
        fm.fmeda_fit = 20.0

        be = FaultTreeNode("BE", "Basic Event")
        be.failure_mode_ref = fm.unique_id
        be.prob_formula = "linear"

        app = DummyApp(fm)
        prob = AutoMLApp.compute_failure_prob(app, be)
        expected = (20.0 / 4) / 1e9
        self.assertAlmostEqual(prob, expected)

if __name__ == "__main__":
    unittest.main()
