from types import SimpleNamespace
from pathlib import Path
import sys
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
        self.oval_coords = None

    def create_oval(self, x1, y1, x2, y2, **kwargs):
        self.oval_coords = (x1, y1, x2, y2)

    def create_text(self, *args, **kwargs):
        pass

    def create_polygon(self, *args, **kwargs):
        pass

    def create_rectangle(self, *args, **kwargs):
        pass

    def create_line(self, *args, **kwargs):
        pass


@pytest.fixture
def dummy_window(monkeypatch):
    monkeypatch.setattr(tkFont, "Font", lambda *a, **k: DummyFont())
    StyleManager._instance = None
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.zoom = 1
    win.canvas = DummyCanvas()
    win.drawing_helper = SimpleNamespace(_fill_gradient_oval=lambda *a, **k: None)
    win.font = DummyFont()
    win.selected_objs = set()
    win.repo = SimpleNamespace(
        elements={}, diagrams={}, element_diagrams={}, relationships=[], get_linked_diagram=lambda _id: None
    )
    win.diagram_id = "D1"
    return win


def test_use_case_draws_oval(dummy_window):
    class DummyObj(SimpleNamespace):
        __hash__ = object.__hash__

    obj = DummyObj(
        obj_type="Use Case",
        x=0,
        y=0,
        width=100,
        height=60,
        obj_id=1,
        properties={},
        element_id=None,
        phase="",
        requirements=[],
    )
    dummy_window.draw_object(obj)
    x1, y1, x2, y2 = dummy_window.canvas.oval_coords
    assert x2 - x1 == pytest.approx(100)
    assert y2 - y1 == pytest.approx(60)
