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

import os
import sys
import types
from unittest import mock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp
from gui.architecture import (
    UseCaseDiagramWindow,
    SysMLDiagramWindow,
    SysMLObject,
    _get_next_id,
    ARCH_WINDOWS,
)
import gui.architecture as architecture


class DummyRepo:
    def __init__(self):
        self.diagrams = {
            1: types.SimpleNamespace(
                diag_id=1, diag_type="Use Case Diagram", objects=[], connections=[]
            )
        }

    def push_undo_state(self, sync_app=False):
        pass

    def object_visible(self, obj, did):
        return True

    def connection_visible(self, conn, did):
        return True

    def touch_diagram(self, diag_id):
        pass

    def visible_objects(self, diag_id):
        return self.diagrams[diag_id].objects

    def visible_connections(self, diag_id):
        return []


def test_context_menu_edit_keeps_diagram_objects():
    ARCH_WINDOWS.clear()
    app = AutoMLApp.__new__(AutoMLApp)
    app.update_views = lambda: None
    repo = DummyRepo()

    win = UseCaseDiagramWindow.__new__(UseCaseDiagramWindow)
    win.app = app
    win.repo = repo
    win.diagram_id = 1
    win.objects = []
    win.connections = []
    win.redraw = lambda: None
    win.update_property_view = lambda: None
    win.sort_objects = lambda: None

    obj = SysMLObject(
        obj_id=_get_next_id(),
        obj_type="Actor",
        x=0,
        y=0,
        element_id=None,
        width=40,
        height=80,
        properties={"name": "A"},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )
    win.objects.append(obj)

    win._sync_to_repository = types.MethodType(
        SysMLDiagramWindow._sync_to_repository, win
    )
    win.refresh_from_repository = types.MethodType(
        SysMLDiagramWindow.refresh_from_repository, win
    )
    win._on_focus_in = types.MethodType(SysMLDiagramWindow._on_focus_in, win)

    class DummyDialog:
        def __init__(self, master, obj):
            master._on_focus_in()

    with (
        mock.patch.object(architecture, "SysMLObjectDialog", DummyDialog),
        mock.patch.object(architecture, "update_block_parts_from_ibd", lambda repo, diag: None),
        mock.patch.object(architecture, "_sync_block_parts_from_ibd", lambda repo, diag_id: None),
        mock.patch.object(
            architecture,
            "_enforce_ibd_multiplicity",
            lambda repo, block_id, app=None: [],
        ),
    ):
        win._edit_object(obj)

    assert len(win.objects) == 1
    assert repo.diagrams[1].objects, "Actor should persist in repository"
