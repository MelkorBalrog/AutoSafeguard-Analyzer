import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Block Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id

class AggregationGeneralizationRuleTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_duplicate_aggregation_prevented(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Aggregation", parent.elem_id, part.elem_id)
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        win = DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=child.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=part.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Aggregation")
        self.assertFalse(valid)

    def test_duplicate_composite_prevented(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Composite Aggregation", parent.elem_id, part.elem_id)
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        win = DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=child.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=part.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Composite Aggregation")
        self.assertFalse(valid)

if __name__ == "__main__":
    unittest.main()
