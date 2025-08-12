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
from sysml.sysml_repository import SysMLRepository

class HazardSeverityUndoRedoTests(unittest.TestCase):
    def setUp(self):
        self.app = FaultTreeApp.__new__(FaultTreeApp)
        self.app.hazard_severity = {"H1": 1}
        self.app.hazards = ["H1"]
        self.app.hara_docs = []
        self.app.fi2tc_docs = []
        self.app.tc2fi_docs = []
        self.app.update_views = lambda: None
        self.app._undo_stack = []
        self.app._redo_stack = []
        self.app.export_model_data = lambda include_versions=False: {
            "hazard_severity": self.app.hazard_severity.copy()
        }
        def apply_model_data(state):
            self.app.hazard_severity = state["hazard_severity"].copy()
        self.app.apply_model_data = apply_model_data
        SysMLRepository.reset_instance()

    def test_undo_redo_update_hazard_severity(self):
        self.app.update_hazard_severity("H1", 5)
        self.assertEqual(self.app.hazard_severity["H1"], 5)
        self.app.undo()
        self.assertEqual(self.app.hazard_severity["H1"], 1)
        self.app.redo()
        self.assertEqual(self.app.hazard_severity["H1"], 5)

if __name__ == "__main__":
    unittest.main()
