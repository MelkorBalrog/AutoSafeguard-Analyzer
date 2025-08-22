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

        def all_nodes(_self, node=None):
            return [self.original, self.clone]

        self.app.get_all_nodes = types.MethodType(all_nodes, self.app)
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

        self.original.manager_notes = "NewNote"
        self.app.sync_nodes_by_id(self.original)
        self.assertEqual(self.clone.manager_notes, "NewNote")


if __name__ == "__main__":
    unittest.main()
