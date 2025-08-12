import unittest
from analysis.utils import (
    derive_validation_target,
    exposure_to_probability,
    controllability_to_probability,
    severity_to_probability,
)
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
        node.exposure = 4
        node.controllability = 3
        node.severity = 2
        node.update_validation_target()
        self.assertAlmostEqual(node.validation_target, 2e-4)

    def test_probability_mappings(self):
        self.assertAlmostEqual(exposure_to_probability(4), 5e-2)
        self.assertAlmostEqual(controllability_to_probability(3), 1e-1)
        self.assertAlmostEqual(severity_to_probability(2), 1e-2)

if __name__ == "__main__":
    unittest.main()
