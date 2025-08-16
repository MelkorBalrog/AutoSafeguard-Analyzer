import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.architecture import SysMLObject, SysMLDiagramWindow


class DummyCanvas:
    def __init__(self):
        self.text_calls = []

    def create_rectangle(self, *args, **kwargs):
        pass

    def create_line(self, *args, **kwargs):
        pass

    def create_text(self, x, y, *args, **kwargs):
        self.text_calls.append((x, y, kwargs))


def test_testsuite_label_position():
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.canvas = DummyCanvas()
    win.zoom = 1.0
    win.font = ("Arial", 12)
    win.selected_objs = []
    win._object_label_lines = lambda obj: [obj.properties.get("name", "")]

    obj = SysMLObject(
        1,
        "Test Suite",
        100,
        100,
        width=80,
        height=40,
        properties={"name": "TS"},
    )
    win.draw_object(obj)

    assert win.canvas.text_calls, "No text drawn for test suite label"
    x, y, kw = win.canvas.text_calls[-1]
    assert kw.get("text") == "TS"
    expected_y = obj.y * win.zoom + obj.height * win.zoom / 2 + 10 * win.zoom
    assert x == obj.x * win.zoom
    assert y == pytest.approx(expected_y)
