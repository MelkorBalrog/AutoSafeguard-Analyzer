import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository

class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)
    def metrics(self, name: str) -> int:
        return 1

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        self.zoom = 1.0
        self.font = DummyFont()

    _block_compartments = SysMLDiagramWindow._block_compartments

class BlockCompartmentTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_parts_include_block_name(self):
        parent = self.repo.create_element("Block", name="Parent", properties={"partProperties": "P"})
        child = self.repo.create_element("Block", name="Child")
        self.repo.create_element("Part", name="P", properties={"definition": child.elem_id})
        obj = SysMLObject(
            1,
            "Block",
            0,
            0,
            element_id=parent.elem_id,
            properties={"name": "Parent", "partProperties": "P"},
        )
        win = DummyWindow()
        compartments = win._block_compartments(obj)
        self.assertIn(("Parts", "P : Child"), compartments)

if __name__ == "__main__":
    unittest.main()
