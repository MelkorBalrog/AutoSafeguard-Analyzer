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
    def create_text(self, *args, **kwargs):
        pass


@pytest.fixture
def window(monkeypatch):
    monkeypatch.setattr(tkFont, "Font", lambda *a, **k: DummyFont())
    StyleManager._instance = None
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.zoom = 1
    win.canvas = DummyCanvas()
    win.font = DummyFont()
    win.gradient_cache = {}
    win.drawing_helper = SimpleNamespace()
    win.selected_objs = set()
    win.repo = SimpleNamespace(
        elements={}, diagrams={}, element_diagrams={}, relationships=[], get_linked_diagram=lambda _id: None
    )
    win.diagram_id = "D1"
    return win


def test_cylinder_shapes_use_common_draw(window, monkeypatch):
    calls = []
    monkeypatch.setattr(window, "_draw_cylinder", lambda *args, **kwargs: calls.append(args))
    for t in ["Data", "Field Data", "AI Database"]:
        class Obj(SimpleNamespace):
            __hash__ = object.__hash__

        obj = Obj(
            obj_type=t,
            x=0,
            y=0,
            width=40,
            height=20,
            obj_id=1,
            properties={},
            element_id=None,
            phase="",
            requirements=[],
            locked=False,
            hidden=False,
            collapsed={},
        )
        window.draw_object(obj)
    assert len(calls) == 3

