import sys
from pathlib import Path
from types import SimpleNamespace
import tkinter.font as tkFont

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLDiagramWindow
from gui.style_manager import StyleManager


class DummyFont:
    def configure(self, **kwargs):
        pass


class DummyCanvas:
    def __init__(self):
        self.text_calls = []

    def create_oval(self, *args, **kwargs):
        pass

    def create_polygon(self, *args, **kwargs):
        pass

    def create_text(self, x, y, text="", font=None, **kwargs):
        self.text_calls.append(text)


@pytest.fixture
def dummy_window(monkeypatch):
    monkeypatch.setattr(tkFont, "Font", lambda *a, **k: DummyFont())
    StyleManager._instance = None
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.zoom = 1
    win.canvas = DummyCanvas()
    win.drawing_helper = SimpleNamespace(_fill_gradient_circle=lambda *a, **k: None)
    win.font = DummyFont()
    win.selected_objs = set()
    win.repo = SimpleNamespace(elements={}, diagrams={}, element_diagrams={}, relationships=[], get_linked_diagram=lambda _id: None)
    win.diagram_id = "D1"
    return win


def test_standard_shape_has_iso_label(dummy_window):
    class DummyObj(SimpleNamespace):
        __hash__ = object.__hash__

    obj = DummyObj(
        obj_type="Standard",
        x=0,
        y=0,
        width=100,
        height=100,
        obj_id=1,
        properties={},
        element_id=None,
        phase="",
        requirements=[],
    )
    dummy_window.draw_object(obj)
    assert "ISO/IEEE/IEC" in dummy_window.canvas.text_calls
