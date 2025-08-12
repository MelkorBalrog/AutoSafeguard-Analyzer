import unittest
from analysis.safety_management import SafetyWorkProduct, LifecyclePhase, SafetyGovernance, Workflow


class SafetyManagementTests(unittest.TestCase):
    def test_work_product_added_to_phase(self):
        phase = LifecyclePhase(name="Concept")
        wp = SafetyWorkProduct(name="HAZOP", source="Hazop Analysis", rationale="Identify hazards")
        phase.work_products.append(wp)
        self.assertEqual(len(phase.work_products), 1)
        self.assertEqual(phase.work_products[0].rationale, "Identify hazards")

    def test_workflow_steps(self):
        gov = SafetyGovernance()
        wf = Workflow(name="Review", steps=["plan", "execute"])
        gov.workflows.append(wf)
        self.assertEqual(gov.workflows[0].steps, ["plan", "execute"])

if __name__ == "__main__":
    unittest.main()
