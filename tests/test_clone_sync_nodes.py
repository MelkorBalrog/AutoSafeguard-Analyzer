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
from AutoML import FaultTreeApp, FaultTreeNode


class CloneSyncTests(unittest.TestCase):
    def setUp(self):
        self.app = FaultTreeApp.__new__(FaultTreeApp)
        self.app.fmea_entries = []
        self.app.fmeas = []
        self.app.fmedas = []

        self.original = FaultTreeNode("orig", "Basic Event")
        self.original.display_label = "OrigLabel"
        self.clone1 = self.app.clone_node_preserving_id(self.original)
        self.clone2 = self.app.clone_node_preserving_id(self.original)

        # stub methods used by sync_nodes_by_id
        def all_nodes(_self, node=None):
            return [self.original, self.clone1, self.clone2]
        self.app.get_all_nodes = types.MethodType(all_nodes, self.app)
        self.app.get_all_fmea_entries = types.MethodType(lambda _self: [], self.app)
        self.app.root_node = self.original

        # initial sync to apply clone markers
        self.app.sync_nodes_by_id(self.original)

    def test_clone_and_original_propagation(self):
        # modify a clone and sync
        self.clone1.user_name = "Updated"
        self.clone1.display_label = "UpdatedLabel (clone)"
        self.app.sync_nodes_by_id(self.clone1)

        # original and other clones should update
        self.assertEqual(self.original.user_name, "Updated")
        self.assertEqual(self.original.display_label, "UpdatedLabel")
        self.assertEqual(self.clone2.user_name, "Updated")
        self.assertEqual(self.clone2.display_label, "UpdatedLabel (clone)")

        # modify the original and propagate to clones
        self.original.description = "New description"
        self.app.sync_nodes_by_id(self.original)
        self.assertEqual(self.clone1.description, "New description")
        self.assertEqual(self.clone2.description, "New description")


if __name__ == "__main__":  # pragma: no cover - manual test execution
    unittest.main()
