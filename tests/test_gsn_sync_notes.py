import types
import os
import sys
import unittest

# Provide dummy PIL modules to allow AutoML import without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp
from gsn import GSNNode


class GSNCloneSyncNotesTests(unittest.TestCase):
    def setUp(self):
        self.app = AutoMLApp.__new__(AutoMLApp)
        self.app.fmea_entries = []
        self.app.fmeas = []
        self.app.fmedas = []
        self.original = GSNNode("Orig", "Goal")
        self.clone = self.original.clone()

        # Simulate a traversal that misses detached clones (real-world bug)
        def all_nodes(_self, node=None):
            return [self.original]

        # Model-wide query still sees both nodes
        def all_nodes_in_model(_self):
            return [self.original, self.clone]

        self.app.get_all_nodes = types.MethodType(all_nodes, self.app)
        self.app.get_all_nodes_in_model = types.MethodType(all_nodes_in_model, self.app)
        self.app.get_all_fmea_entries = types.MethodType(lambda _self: [], self.app)
        self.app.root_node = self.original

    def test_sync_notes_and_description(self):
        self.clone.user_name = "Updated"
        self.clone.description = "Desc"
        self.clone.manager_notes = "Note"
        self.app.sync_nodes_by_id(self.clone)
        self.assertEqual(self.original.user_name, "Updated")
        self.assertEqual(self.original.description, "Desc")
        self.assertEqual(self.original.manager_notes, "Note")

        self.original.user_name = "OrigUpdated"
        self.original.description = "OrigDesc"
        self.original.manager_notes = "NewNote"
        self.app.sync_nodes_by_id(self.original)
        self.assertEqual(self.clone.user_name, "OrigUpdated")
        self.assertEqual(self.clone.description, "OrigDesc")
        self.assertEqual(self.clone.manager_notes, "NewNote")

    def test_original_syncs_clone_when_model_missing(self):
        self.app.get_all_nodes_in_model = types.MethodType(lambda _self: [self.original], self.app)
        diag = types.SimpleNamespace(nodes=[self.original, self.clone])
        self.app.gsn_diagrams = [diag]
        self.app.all_gsn_diagrams = [diag]
        self.original.description = "OrigDesc"
        self.original.user_name = "OrigName"
        self.original.manager_notes = "OrigNote"
        self.app.sync_nodes_by_id(self.original)
        self.assertEqual(self.clone.description, "OrigDesc")
        self.assertEqual(self.clone.user_name, "OrigName")
        self.assertEqual(self.clone.manager_notes, "OrigNote")


if __name__ == "__main__":
    unittest.main()
