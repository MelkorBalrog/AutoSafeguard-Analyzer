import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Internal Block Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.objects = []
        self.connections = []
        self.selected_obj = None

    def _sync_to_repository(self):
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [obj.__dict__ for obj in self.objects]
            diag.connections = [conn.__dict__ for conn in self.connections]

    def redraw(self):
        pass

    def update_property_view(self):
        pass

class RemovePartVisibilityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_remove_part_diagram_marks_hidden(self):
        win = DummyWindow()
        part = SysMLObject(1, "Part", 0, 0)
        win.objects = [part]
        SysMLDiagramWindow.remove_part_diagram(win, part)
        self.assertIn(part, win.objects)
        self.assertTrue(part.hidden)

if __name__ == "__main__":
    unittest.main()
