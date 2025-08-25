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

import copy
import types

from gui.architecture import SysMLDiagramWindow, SysMLObject, _get_next_id


class DummyRepo:
    def __init__(self, diag_type):
        self.diagrams = {1: types.SimpleNamespace(diag_type=diag_type, elements=[])}

    def diagram_read_only(self, _id):
        return False


def _make_window(app, repo):
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.app = app
    win.repo = repo
    win.diagram_id = 1
    win.objects = []
    win.selected_obj = None
    win.remove_object = lambda o: win.objects.remove(o)
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.update_property_view = lambda: None
    win.sort_objects = lambda: None
    win.refresh_from_repository = lambda e=None: None
    win._constrain_to_parent = lambda *a, **k: None
    win._place_process_area = lambda name, x, y: SysMLObject(
        obj_id=_get_next_id(),
        obj_type="System Boundary",
        x=x,
        y=y,
        element_id=None,
        width=80,
        height=40,
        properties={"name": name},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )
    win._on_focus_in = types.MethodType(SysMLDiagramWindow._on_focus_in, win)
    return win


def test_sysml_clone_and_paste():
    app = types.SimpleNamespace(diagram_clipboard=None, diagram_clipboard_type=None)
    repo = DummyRepo("Governance Diagram")
    obj = SysMLObject(
        obj_id=_get_next_id(),
        obj_type="Plan",
        x=0,
        y=0,
        element_id=None,
        width=80,
        height=40,
        properties={},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )

    win1 = _make_window(app, repo)
    win1.objects = [obj]
    win1.selected_obj = obj

    snap1 = win1._clone_object_strategy1(obj)
    snap2 = win1._clone_object_strategy2(obj)
    snap3 = win1._clone_object_strategy3(obj)
    snap4 = win1._clone_object_strategy4(obj)
    assert snap1 == snap2 == snap3 == snap4

    win1.copy_selected()
    assert app.diagram_clipboard == snap1
    assert app.diagram_clipboard_type == "Governance Diagram"

    win2 = _make_window(app, repo)

    for strat in (
        win2._reconstruct_object_strategy1,
        win2._reconstruct_object_strategy2,
        win2._reconstruct_object_strategy3,
        win2._reconstruct_object_strategy4,
    ):
        app.diagram_clipboard = copy.deepcopy(snap1)
        new_obj = strat(app.diagram_clipboard)
        assert new_obj.x == snap1["x"] + 20

    app.diagram_clipboard = snap1
    win2.paste_selected()
    assert len(win2.objects) == 1
    assert win2.objects[0] is not obj

