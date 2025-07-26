# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from analysis.fmeda_utils import compute_fmeda_metrics
from analysis.models import ReliabilityComponent

class DummyNode:
    def __init__(self, comp, ftype, frac, fit, diag_cov=0.0, sg=""):
        self.parents = []
        if comp:
            parent = type("P", (), {"user_name": comp})
            self.parents.append(parent)
        self.fmea_component = comp or ""
        self.fmeda_fault_type = ftype
        self.fmeda_fault_fraction = frac
        self.fmeda_fit = fit
        self.fmeda_diag_cov = diag_cov
        self.fmeda_safety_goal = sg

class MetricsTests(unittest.TestCase):
    def test_basic_metrics(self):
        comp = ReliabilityComponent("C1", "resistor", quantity=1)
        comp.fit = 10.0
        nodes = [
            DummyNode("C1", "permanent", 1.0, 10.0, diag_cov=0.5, sg="SG1"),
            DummyNode("C1", "transient", 1.0, 5.0, diag_cov=0.2, sg="SG1"),
        ]
        def sg_to_asil(_):
            return "B"
        metrics = compute_fmeda_metrics(nodes, [comp], sg_to_asil)
        self.assertAlmostEqual(metrics["total"], 20.0)
        self.assertAlmostEqual(metrics["spfm_raw"], 5.0)
        self.assertAlmostEqual(metrics["lpfm_raw"], 8.0)
        self.assertAlmostEqual(metrics["dc"], (20.0 - 13.0)/20.0)
        self.assertEqual(metrics["asil"], "B")

    def test_goal_targets(self):
        comp = ReliabilityComponent("C1", "resistor", quantity=1)
        comp.fit = 10.0
        nodes = [
            DummyNode("C1", "permanent", 1.0, 10.0, diag_cov=1.0, sg="SG1"),
        ]
        def sg_to_asil(_):
            return "C"
        targets = {"SG1": {"dc": 0.9, "spfm": 0.97, "lpfm": 0.9}}
        metrics = compute_fmeda_metrics(nodes, [comp], sg_to_asil, sg_targets=targets)
        gm = metrics["goal_metrics"]["SG1"]
        self.assertTrue(gm["ok_dc"])
        self.assertTrue(gm["ok_spfm"])
        self.assertTrue(gm["ok_lpfm"])

if __name__ == "__main__":
    unittest.main()
