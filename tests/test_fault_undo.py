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

class FaultUndoRedoTests(unittest.TestCase):
    def setUp(self):
        self.app = FaultTreeApp.__new__(FaultTreeApp)
        # Minimal attributes for export_model_data
        self.app.top_events = []
        self.app.fmeas = []
        self.app.fmedas = []
        self.app.mechanism_libraries = []
        self.app.selected_mechanism_libraries = []
        self.app.mission_profiles = []
        self.app.reliability_analyses = []
        self.app.hazop_docs = []
        self.app.hara_docs = []
        self.app.stpa_docs = []
        self.app.threat_docs = []
        self.app.fi2tc_docs = []
        self.app.tc2fi_docs = []
        self.app.hazop_entries = []
        self.app.fi2tc_entries = []
        self.app.tc2fi_entries = []
        self.app.fmea_entries = []
        self.app.fmeda_entries = []
        self.app.scenario_libraries = []
        self.app.odd_libraries = []
        self.app.faults = []
        self.app.malfunctions = []
        self.app.hazards = []
        self.app.failures = []
        self.app.project_properties = {}
        self.app.reviews = []
        self.app.review_data = None
        self.app.global_requirements = []
        self.app.versions = {}
        self.app.update_odd_elements = lambda: None
        self.app.update_views = lambda: None
        self.app._undo_stack = []
        self.app._redo_stack = []
        SysMLRepository.reset_instance()

    def test_undo_redo_add_fault(self):
        self.app.add_fault("F1")
        self.assertIn("F1", self.app.faults)
        self.app.undo()
        self.assertNotIn("F1", self.app.faults)
        self.app.redo()
        self.assertIn("F1", self.app.faults)

if __name__ == "__main__":
    unittest.main()
