import os
import sys
import types
import unittest

# Create a minimal stub for the PIL module so that importing AutoML does not
# require the external Pillow dependency during tests.
PIL_stub = types.ModuleType("PIL")
PIL_stub.Image = object
PIL_stub.ImageTk = object
PIL_stub.ImageDraw = object
PIL_stub.ImageFont = object
sys.modules.setdefault("PIL", PIL_stub)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from AutoML import FaultTreeApp


class DummyNode:
    def __init__(self, unique_id, node_type, name, gate_type=None, children=None, input_subtype=""):
        self.unique_id = unique_id
        self.node_type = node_type
        self.name = name
        self.gate_type = gate_type
        self.children = children or []
        self.input_subtype = input_subtype


class CauseEffectDiagramTests(unittest.TestCase):
    def setUp(self):
        # Create a minimal FaultTreeApp instance without initialising Tk
        self.app = FaultTreeApp.__new__(FaultTreeApp)

    def test_build_simplified_fta_model_includes_basic_events(self):
        be1 = DummyNode(2, "BASIC EVENT", "Cause 1")
        be2 = DummyNode(3, "BASIC EVENT", "Cause 2")
        top = DummyNode(1, "TOP EVENT", "Hazard", gate_type="AND", children=[be1, be2])

        model = self.app.build_simplified_fta_model(top)

        node_ids = {n["id"] for n in model["nodes"]}
        self.assertEqual(node_ids, {"1", "2", "3"})

        edge_pairs = {(e["source"], e["target"]) for e in model["edges"]}
        self.assertEqual(edge_pairs, {("1", "2"), ("1", "3")})


if __name__ == "__main__":
    unittest.main()
