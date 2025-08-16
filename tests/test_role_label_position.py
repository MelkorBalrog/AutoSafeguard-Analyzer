import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gui.architecture import SysMLObject, SysMLDiagramWindow

class DummyCanvas:
    def __init__(self):
        self.text_calls = []
    def create_oval(self, *args, **kwargs):
        pass
    def create_line(self, *args, **kwargs):
        pass
    def create_text(self, x, y, *args, **kwargs):
        self.text_calls.append((x, y, kwargs))
    def create_rectangle(self, *args, **kwargs):
        pass


def test_role_label_position():
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.canvas = DummyCanvas()
    win.zoom = 1.0
    win.font = ("Arial", 12)
    win.selected_objs = []
    # stub out label line generation to avoid repository dependencies
    win._object_label_lines = lambda obj: [obj.properties.get("name", "")]

    obj = SysMLObject(1, "Role", 100, 100, width=80, height=40, properties={"name": "Operator"})
    win.draw_object(obj)

    assert win.canvas.text_calls, "No text drawn for role label"
    x, y, kw = win.canvas.text_calls[-1]
    assert kw.get("anchor") == "n"
    assert kw.get("text") == "Operator"
    sy = obj.height / 40.0 * win.zoom
    expected_y = obj.y * win.zoom + 40 * sy + 10 * win.zoom
    assert x == obj.x * win.zoom
    assert y == pytest.approx(expected_y)
