import unittest
from analysis.utils import derive_validation_target
from analysis.risk_assessment import calculate_validation_target
from AutoML import FaultTreeNode


class ValidationTargetTests(unittest.TestCase):
    def test_derive_validation_target_example(self):
        rate = derive_validation_target(1e-8, 0.05, 0.1, 0.01)
        self.assertAlmostEqual(rate, 2e-4)

    def test_invalid_probabilities(self):
        with self.assertRaises(ValueError):
            derive_validation_target(1e-8, 0.0, 0.1, 0.01)

    def test_wrapper(self):
        rate = calculate_validation_target(1e-8, 0.05, 0.1, 0.01)
        self.assertAlmostEqual(rate, 2e-4)

    def test_fault_tree_node_update(self):
        node = FaultTreeNode("SG1", "TOP EVENT")
        node.acceptance_rate = 1e-8
        node.exposure_given_hb = 0.05
        node.uncontrollable_given_exposure = 0.1
        node.severity_given_uncontrollable = 0.01
        node.update_validation_target()
        self.assertAlmostEqual(node.validation_target, 2e-4)


if __name__ == "__main__":
    unittest.main()
