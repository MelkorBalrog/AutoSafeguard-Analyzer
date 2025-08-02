import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyCanvas:
    def __init__(self):
        self.texts = []

    def create_text(self, *args, **kwargs):
        self.texts.append((args, kwargs))

    def create_image(self, *args, **kwargs):
        pass

    def create_rectangle(self, *args, **kwargs):
        pass

    def create_polygon(self, *args, **kwargs):
        pass

    def create_line(self, *args, **kwargs):
        pass

    def create_oval(self, *args, **kwargs):
        pass


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.zoom = 1
        self.font = None
        self.canvas = DummyCanvas()
        self.gradient_cache = {}
        self.selected_objs = []
        self.selected_obj = None
        self._draw_gradient_rect = lambda *args, **kwargs: None
        self._create_round_rect = lambda *args, **kwargs: None
        self._draw_subdiagram_marker = lambda *args, **kwargs: None


class ControlFlowLabelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_existing_element_single_label(self):
        win = DummyWindow()
        element = win.repo.create_element("Block", name="Controller")
        win.repo.add_element_to_diagram(win.diagram_id, element.elem_id)
        obj = SysMLObject(
            1,
            "Existing Element",
            10,
            20,
            width=40,
            height=20,
            element_id=element.elem_id,
            properties={"name": element.name},
        )
        SysMLDiagramWindow.draw_object(win, obj)
        self.assertEqual(len(win.canvas.texts), 1)
        args, kwargs = win.canvas.texts[0]
        self.assertEqual((args[0], args[1]), (obj.x, obj.y))
        self.assertEqual(kwargs.get("anchor"), "center")


if __name__ == "__main__":
    unittest.main()
