import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)

    def metrics(self, name: str) -> int:
        return 1


class DummyWindow:
    _object_label_lines = SysMLDiagramWindow._object_label_lines

    def __init__(self, diag_id):
        self.repo = SysMLRepository.get_instance()
        self.zoom = 1.0
        self.font = DummyFont()
        self.diagram_id = diag_id


class BoundaryStereotypeLabelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()

    def test_block_boundary_label_omits_stereotype(self):
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Governance Diagram")
        elem = repo.create_element("Block", name="Boundary")
        obj = SysMLObject(
            1,
            "Block Boundary",
            0.0,
            0.0,
            element_id=elem.elem_id,
            properties={"name": "Boundary"},
        )
        win = DummyWindow(diag.diag_id)
        self.assertEqual(["Boundary"], win._object_label_lines(obj))

    def test_system_boundary_label_omits_stereotype(self):
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Governance Diagram")
        elem = repo.create_element("System", name="System")
        obj = SysMLObject(
            1,
            "System Boundary",
            0.0,
            0.0,
            element_id=elem.elem_id,
            properties={"name": "System"},
        )
        win = DummyWindow(diag.diag_id)
        self.assertEqual(["System"], win._object_label_lines(obj))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
