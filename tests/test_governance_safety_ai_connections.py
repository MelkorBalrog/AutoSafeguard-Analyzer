import unittest
import types

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class GovernanceSafetyAIConnectionTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def tearDown(self):
        SysMLRepository.reset_instance()

    def _window(self, diag):
        return types.SimpleNamespace(repo=self.repo, diagram_id=diag.diag_id)

    def _make_nodes(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        gobj = SysMLObject(1, "Action", 0, 0, element_id=e1.elem_id)
        aiobj = SysMLObject(2, "Database", 0, 100, element_id=e2.elem_id)
        diag.objects = [gobj.__dict__, aiobj.__dict__]
        return diag, gobj, aiobj

    def _make_ai_pair(self, src_type, dst_type):
        repo = self.repo
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        src = SysMLObject(1, src_type, 0, 0, element_id=e1.elem_id)
        dst = SysMLObject(2, dst_type, 0, 100, element_id=e2.elem_id)
        diag.objects = [src.__dict__, dst.__dict__]
        return diag, src, dst

    def test_safety_ai_relationship_between_governance_and_ai(self):
        diag, gobj, aiobj = self._make_nodes()
        win = self._window(diag)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, gobj, aiobj, "Annotation")
        self.assertTrue(valid)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, aiobj, gobj, "Annotation")
        self.assertTrue(valid)

    def test_flow_from_governance_to_ai_allowed(self):
        diag, gobj, aiobj = self._make_nodes()
        win = self._window(diag)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, gobj, aiobj, "Flow")
        self.assertTrue(valid)

    def test_ai_training_direction(self):
        diag, db, ann = self._make_ai_pair("Database", "ANN")
        win = self._window(diag)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, db, ann, "AI training")
        self.assertTrue(valid)
        diag, ann, db = self._make_ai_pair("ANN", "Database")
        win = self._window(diag)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, ann, db, "AI training")
        self.assertFalse(valid)

    def test_model_evaluation_direction(self):
        diag, ann, db = self._make_ai_pair("ANN", "Database")
        win = self._window(diag)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, ann, db, "Model evaluation")
        self.assertTrue(valid)
        diag, db, ann = self._make_ai_pair("Database", "ANN")
        win = self._window(diag)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, db, ann, "Model evaluation")
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
