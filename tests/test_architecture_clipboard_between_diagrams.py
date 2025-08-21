import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow, _get_next_id, _DIAGRAM_CLIPBOARDS
from sysml.sysml_repository import SysMLRepository


class DummyWindow:
    copy_selected = SysMLDiagramWindow.copy_selected
    cut_selected = SysMLDiagramWindow.cut_selected
    paste_selected = SysMLDiagramWindow.paste_selected

    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.diagram_type = diagram.diag_type
        self.objects = []
        self.connections = []
        self.selected_obj = None
        self.selected_objs = []

    def redraw(self):
        pass

    def update_property_view(self):
        pass

    def sort_objects(self):
        pass

    def _sync_to_repository(self):
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [o.__dict__ for o in self.objects]

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            self._sync_to_repository()


class ArchitectureClipboardTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()
        _DIAGRAM_CLIPBOARDS.clear()

    def test_copy_paste_between_same_type_diagrams(self):
        d1 = self.repo.create_diagram("Block Diagram")
        d2 = self.repo.create_diagram("Block Diagram")
        w1, w2 = DummyWindow(d1), DummyWindow(d2)
        obj = SysMLObject(_get_next_id(), "Block", 0, 0)
        w1.objects.append(obj)
        w1.selected_obj = obj
        w1.copy_selected()
        w2.paste_selected()
        self.assertEqual(len(w2.objects), 1)

    def test_cut_paste_between_same_type_diagrams(self):
        d1 = self.repo.create_diagram("Block Diagram")
        d2 = self.repo.create_diagram("Block Diagram")
        w1, w2 = DummyWindow(d1), DummyWindow(d2)
        obj = SysMLObject(_get_next_id(), "Block", 0, 0)
        w1.objects.append(obj)
        w1.selected_obj = obj
        w1.cut_selected()
        self.assertEqual(len(w1.objects), 0)
        w2.paste_selected()
        self.assertEqual(len(w2.objects), 1)


if __name__ == "__main__":
    unittest.main()
