import unittest
import types
import os
import sys

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import FaultTreeApp
from gsn.nodes import GSNNode


class CloneGSNNodeTests(unittest.TestCase):
    def test_clone_preserves_gsn_node_attributes(self):
        app = FaultTreeApp.__new__(FaultTreeApp)
        original = GSNNode("goal", "Goal")
        clone = app.clone_node_preserving_id(original)
        self.assertIsInstance(clone, GSNNode)
        self.assertEqual(clone.user_name, original.user_name)
        self.assertIs(clone.original, original)
        self.assertEqual(clone.x, original.x + 100)
        self.assertEqual(clone.y, original.y + 100)
        self.assertNotEqual(clone.unique_id, original.unique_id)


if __name__ == "__main__":  # pragma: no cover - manual test execution
    unittest.main()
