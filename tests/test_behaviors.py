import unittest
from gui.architecture import parse_behaviors, behaviors_to_json, BehaviorAssignment

class BehaviorParseTests(unittest.TestCase):
    def test_round_trip(self):
        b = BehaviorAssignment("op1", "diag1")
        js = behaviors_to_json([b])
        parsed = parse_behaviors(js)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].operation, "op1")
        self.assertEqual(parsed[0].diagram, "diag1")

if __name__ == '__main__':
    unittest.main()
