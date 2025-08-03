import sys
import os
import unittest

import tests.test_cause_effect_diagram as base_stub

# Ensure the shared Pillow stub exposes ImageTk
PIL_stub = sys.modules.get("PIL")
if PIL_stub is None:
    raise RuntimeError("Pillow stub not loaded")
PIL_stub.ImageTk = object

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from AutoML import FaultTreeApp

class CauseEffectPDFTests(unittest.TestCase):
    def setUp(self):
        self.app = FaultTreeApp.__new__(FaultTreeApp)

    def test_render_cause_effect_diagram_size(self):
        row = {
            "hazard": "Hazard",
            "malfunction": "Malfunction",
            "failure_modes": {},
            "faults": set(),
            "fis": set(),
            "tcs": set(),
        }
        img = self.app.render_cause_effect_diagram(row)
        self.assertIsNotNone(img)
        w, h = img.size
        self.assertGreaterEqual(w, 120)
        self.assertGreaterEqual(h, 60)

if __name__ == "__main__":
    unittest.main()
