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
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from mainappsrc.automl_core import AutoMLApp, FaultTreeNode
from analysis.models import HazopDoc, HazopEntry, HaraDoc, HaraEntry
from mainappsrc.subapps.risk_assessment_subapp import RiskAssessmentSubApp


class OddValidationTargetTests(unittest.TestCase):
    def test_traces_validation_targets_from_scenario_description(self):
        app = AutoMLApp.__new__(AutoMLApp)
        app.risk_app = RiskAssessmentSubApp()
        app.scenario_libraries = [
            {
                "name": "Default",
                "scenarios": [
                    {
                        "name": "Pedestrians crossing",
                        "description": "Vehicle approaches [[Intersection]]",
                    }
                ],
            }
        ]
        hazop_entry = HazopEntry(
            function="F", malfunction="M", mtype="No/Not", scenario="Pedestrians crossing",
            conditions="", hazard="H", safety=True, rationale="", covered=False, covered_by=""
        )
        app.hazop_docs = [HazopDoc("HZ", [hazop_entry])]
        hara_entry = HaraEntry(
            malfunction="M", hazard="H", scenario="Pedestrians crossing", severity=1,
            sev_rationale="", controllability=1, cont_rationale="", exposure=1,
            exp_rationale="", asil="QM", safety_goal="PG1"
        )
        app.hara_docs = [HaraDoc("RA", [], [hara_entry])]
        node = FaultTreeNode("PG1", "TOP EVENT")
        node.safety_goal_description = "PG1"
        node.validation_target = 0.5
        node.validation_desc = "desc"
        node.acceptance_criteria = "criteria"
        app.top_events = [node]
        goals = app.get_validation_targets_for_odd("Intersection")
        self.assertEqual(goals, [node])


if __name__ == "__main__":
    unittest.main()
