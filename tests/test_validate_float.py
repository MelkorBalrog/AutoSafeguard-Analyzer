import unittest
from AutoML import FaultTreeApp


class ValidateFloatTests(unittest.TestCase):
    def test_allows_scientific_notation(self):
        self.assertTrue(FaultTreeApp.validate_float(None, "1e"))
        self.assertTrue(FaultTreeApp.validate_float(None, "1e-"))
        self.assertTrue(FaultTreeApp.validate_float(None, "1e-8"))


if __name__ == "__main__":
    unittest.main()
