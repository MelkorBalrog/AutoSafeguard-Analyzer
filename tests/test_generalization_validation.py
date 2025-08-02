import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Block Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id


class GeneralizationValidationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_common_parent_invalid(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        c = repo.create_element("Block", name="C")
        repo.create_relationship("Generalization", a.elem_id, c.elem_id)
        repo.create_relationship("Generalization", b.elem_id, c.elem_id)
        win = DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=a.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=b.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(
            win, src, dst, "Generalization"
        )
        self.assertFalse(valid)

    def test_cycle_invalid(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Generalization", b.elem_id, a.elem_id)
        win = DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=a.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=b.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(
            win, src, dst, "Generalization"
        )
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
