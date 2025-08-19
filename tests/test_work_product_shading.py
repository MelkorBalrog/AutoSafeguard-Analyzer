import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import types
from gui.architecture import GovernanceDiagramWindow, SysMLObject

class DummyCanvas:
    def create_polygon(self, *a, **k):
        pass
    def create_line(self, *a, **k):
        pass
    def create_text(self, *a, **k):
        pass
    def create_arc(self, *a, **k):
        pass
    def create_image(self, *a, **k):
        pass


def test_work_product_shape_uses_gradient():
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.canvas = DummyCanvas()
    win.zoom = 1
    win.font = None
    win.selected_objs = []
    win.repo = types.SimpleNamespace(get_linked_diagram=lambda x: None, diagrams={})
    captured = []
    win._draw_gradient_rect = lambda *args, **kwargs: captured.append(args)
    obj = SysMLObject(obj_id=1, obj_type="Work Product", x=0, y=0, properties={})
    win.draw_object(obj)
    assert captured, "Work Product shape should use gradient fill"
