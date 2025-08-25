# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

