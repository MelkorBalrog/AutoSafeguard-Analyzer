# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from gui.architecture import calculate_allocated_asil
from analysis.models import global_requirements

class PartASILTests(unittest.TestCase):
    def setUp(self):
        global_requirements.clear()

    def test_highest_asil(self):
        global_requirements["R1"] = {"id": "R1", "asil": "B"}
        global_requirements["R2"] = {"id": "R2", "asil": "D"}
        reqs = [global_requirements["R1"], global_requirements["R2"]]
        self.assertEqual(calculate_allocated_asil(reqs), "D")

    def test_missing_asil_defaults_qm(self):
        global_requirements["R3"] = {"id": "R3"}
        reqs = [global_requirements["R3"]]
        self.assertEqual(calculate_allocated_asil(reqs), "QM")

if __name__ == "__main__":
    unittest.main()
