import unittest
from unittest.mock import patch
from gui import architecture
from gui.architecture import BlockDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository

class DummyWindow:
    _add_block_relationships = BlockDiagramWindow._add_block_relationships

    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.objects = []
        self.connections = []
        self.app = None

    def _sync_to_repository(self):
        diag = self.repo.diagrams[self.diagram_id]
        diag.objects = [obj.__dict__ for obj in self.objects]

    def redraw(self):
        pass

    def ensure_text_fits(self, obj):
        pass

class AddBlocksTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_block_from_other_diagram(self):
        repo = self.repo
        block = repo.create_element("Block", name="A")
        d1 = repo.create_diagram("Block Diagram")
        repo.add_element_to_diagram(d1.diag_id, block.elem_id)
        d1.objects.append({
            "obj_id": 1,
            "obj_type": "Block",
            "x": 0,
            "y": 0,
            "element_id": block.elem_id,
            "properties": {"name": "A"},
        })
        d2 = repo.create_diagram("Block Diagram")
        win = DummyWindow(d2)
        class DummyDialog:
            def __init__(self, parent, names, title="Select Blocks"):
                self.result = names
        with patch.object(architecture.SysMLObjectDialog, 'SelectNamesDialog', DummyDialog):
            BlockDiagramWindow.add_blocks(win)
        diag = repo.diagrams[d2.diag_id]
        self.assertEqual(len(diag.objects), 1)
        self.assertEqual(diag.objects[0].get("element_id"), block.elem_id)

if __name__ == '__main__':
    unittest.main()
