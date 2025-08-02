import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui.architecture import SysMLObject, SysMLDiagramWindow
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyWindow:
    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.objects = []
        self.connections = []

    def _sync_to_repository(self):
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [obj.__dict__ for obj in self.objects]
            diag.connections = [conn.__dict__ for conn in self.connections]

    def redraw(self):
        pass

    def update_property_view(self):
        pass

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)


class RemoveElementModelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_remove_element_model(self):
        repo = self.repo
        diag1 = SysMLDiagram(diag_id="d1", diag_type="Block Diagram")
        diag2 = SysMLDiagram(diag_id="d2", diag_type="Block Diagram")
        repo.diagrams[diag1.diag_id] = diag1
        repo.diagrams[diag2.diag_id] = diag2

        block = repo.create_element("Block", name="B")
        obj1 = SysMLObject(1, "Block", 0, 0, element_id=block.elem_id)
        obj2 = {"obj_id": 2, "obj_type": "Block", "x": 0, "y": 0, "element_id": block.elem_id}
        diag2.objects.append(obj2)

        win = DummyWindow(diag1)
        win.objects = [obj1]
        win._sync_to_repository()

        SysMLDiagramWindow.remove_element_model(win, obj1)

        self.assertNotIn(block.elem_id, repo.elements)
        self.assertEqual(len(diag2.objects), 0)


if __name__ == "__main__":
    unittest.main()

