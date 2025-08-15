import os
import sys
import types
import unittest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide dummy PIL modules so tests run without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def configure(self, **kwargs):
        pass


class SafetyAIGovernanceConnectionTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def _window(self, diag):
        win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
        win.repo = self.repo
        win.diagram_id = diag.diag_id
        win.connections = []
        win.canvas = DummyCanvas()
        return win

    def test_safety_ai_relationship_governance_to_ai(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        src = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "Risk Assessment"})
        dst = SysMLObject(2, "Database", 0, 100, element_id=e2.elem_id)
        diag.objects = [src.__dict__, dst.__dict__]
        win = self._window(diag)
        valid, msg = win.validate_connection(src, dst, "Annotation")
        self.assertTrue(valid, msg)

    def test_safety_ai_relationship_ai_to_governance(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        src = SysMLObject(1, "ANN", 0, 0, element_id=e1.elem_id)
        dst = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": "Risk Assessment"})
        diag.objects = [src.__dict__, dst.__dict__]
        win = self._window(diag)
        valid, msg = win.validate_connection(src, dst, "Synthesis")
        self.assertTrue(valid, msg)

    def test_flow_from_action_to_ai(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        src = SysMLObject(1, "Action", 0, 0, element_id=e1.elem_id)
        dst = SysMLObject(2, "Database", 0, 100, element_id=e2.elem_id)
        diag.objects = [src.__dict__, dst.__dict__]
        win = self._window(diag)
        valid, msg = win.validate_connection(src, dst, "Flow")
        self.assertTrue(valid, msg)


if __name__ == "__main__":
    unittest.main()

