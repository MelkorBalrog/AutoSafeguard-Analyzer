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

import csv
import os
import sys
import tempfile
import unittest
from unittest import mock
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Provide minimal PIL stubs to satisfy AutoML imports
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from AutoML import AutoMLApp
from analysis.models import CybersecurityGoal


class CybersecurityGoalTests(unittest.TestCase):
    def test_cal_aggregation(self):
        goal = CybersecurityGoal(
            "CG", "desc", risk_assessments=[
                {"name": "RA1", "cal": "CAL1"},
                {"name": "RA2", "cal": "CAL3"},
                {"name": "RA3", "cal": "CAL2"},
            ]
        )
        goal.compute_cal()
        self.assertEqual(goal.cal, "CAL3")

    def test_export_output(self):
        app = AutoMLApp.__new__(AutoMLApp)
        goal1 = CybersecurityGoal("CG1", "d1", risk_assessments=[{"name": "RA1", "cal": "CAL2"}])
        goal2 = CybersecurityGoal("CG2", "d2", risk_assessments=[{"name": "RA2", "cal": "CAL4"}])
        goal1.compute_cal()
        goal2.compute_cal()
        app.cybersecurity_goals = [goal1, goal2]

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp.close()
        with mock.patch("tkinter.filedialog.asksaveasfilename", return_value=tmp.name), \
             mock.patch("gui.controls.messagebox.showinfo"):
            AutoMLApp.export_cybersecurity_goal_requirements(app)

        with open(tmp.name, newline="") as f:
            rows = list(csv.reader(f))
        os.unlink(tmp.name)

        self.assertEqual(rows[0], ["Cybersecurity Goal", "CAL", "Risk Assessments", "Description"])
        self.assertIn(["CG1", "CAL2", "RA1", "d1"], rows)
        self.assertIn(["CG2", "CAL4", "RA2", "d2"], rows)


if __name__ == "__main__":
    unittest.main()

