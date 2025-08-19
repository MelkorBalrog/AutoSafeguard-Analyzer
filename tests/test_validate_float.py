import unittest
from AutoML import AutoMLApp


class ValidateFloatTests(unittest.TestCase):
    def test_allows_scientific_notation(self):
        self.assertTrue(AutoMLApp.validate_float(None, "1e"))
        self.assertTrue(AutoMLApp.validate_float(None, "1e-"))
        self.assertTrue(AutoMLApp.validate_float(None, "1e-8"))


if __name__ == "__main__":
    unittest.main()
