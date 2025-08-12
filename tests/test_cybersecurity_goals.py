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

from AutoML import FaultTreeApp
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
        app = FaultTreeApp.__new__(FaultTreeApp)
        goal1 = CybersecurityGoal("CG1", "d1", risk_assessments=[{"name": "RA1", "cal": "CAL2"}])
        goal2 = CybersecurityGoal("CG2", "d2", risk_assessments=[{"name": "RA2", "cal": "CAL4"}])
        goal1.compute_cal()
        goal2.compute_cal()
        app.cybersecurity_goals = [goal1, goal2]

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp.close()
        with mock.patch("tkinter.filedialog.asksaveasfilename", return_value=tmp.name), \
             mock.patch("gui.messagebox.showinfo"):
            FaultTreeApp.export_cybersecurity_goal_requirements(app)

        with open(tmp.name, newline="") as f:
            rows = list(csv.reader(f))
        os.unlink(tmp.name)

        self.assertEqual(rows[0], ["Cybersecurity Goal", "CAL", "Risk Assessments", "Description"])
        self.assertIn(["CG1", "CAL2", "RA1", "d1"], rows)
        self.assertIn(["CG2", "CAL4", "RA2", "d2"], rows)


if __name__ == "__main__":
    unittest.main()

