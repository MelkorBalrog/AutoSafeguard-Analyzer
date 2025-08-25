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

import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)

    def metrics(self, name: str) -> int:
        return 1


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y


def _setup_window(repo=None, app=None):
    if repo is None:
        SysMLRepository._instance = None
        repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.canvas = DummyCanvas()
    win.font = DummyFont()
    win.selected_obj = None
    if app is None:
        app = types.SimpleNamespace()
        app.diagram_clipboard = types.SimpleNamespace(
            diagram_clipboard=None,
            diagram_clipboard_type=None,
            diagram_clipboard_parent_name=None,
            clipboard_node=None,
            cut_mode=False,
            clipboard_relation=None,
        )
    win.app = app
    return win


def test_paste_work_product_creates_process_area():
    win = _setup_window()
    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 10.0, 0.0, area=area)
    win.selected_obj = wp
    win.copy_selected()
    assert win.app.diagram_clipboard.diagram_clipboard_parent_name == "Risk Assessment"
    win.selected_obj = None
    win.paste_selected()
    areas = [o for o in win.objects if o.obj_type == "System Boundary"]
    assert len(areas) == 2
    wps = [o for o in win.objects if o.obj_type == "Work Product"]
    assert len(wps) == 2
    pasted_wp = [o for o in wps if o is not wp][0]
    new_area = [a for a in areas if a is not area][0]
    assert pasted_wp.properties.get("parent") == str(new_area.obj_id)
    assert new_area.properties.get("name") == "Risk Assessment"


def test_copy_process_area_includes_children():
    win = _setup_window()
    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 10.0, 0.0, area=area)
    win.selected_obj = area
    win.copy_selected()
    win.selected_obj = None
    win.paste_selected()
    areas = [o for o in win.objects if o.obj_type == "System Boundary"]
    assert len(areas) == 2
    wps = [o for o in win.objects if o.obj_type == "Work Product"]
    assert len(wps) == 2
    pasted_area = [a for a in areas if a is not area][0]
    pasted_wp = [o for o in wps if o is not wp][0]
    assert pasted_wp.properties.get("parent") == str(pasted_area.obj_id)


def test_cut_process_area_includes_children():
    win = _setup_window()
    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win._place_work_product("Risk Assessment", 10.0, 0.0, area=area)
    win.selected_obj = area
    win.cut_selected()
    assert area not in win.objects
    assert wp not in win.objects
    win.selected_obj = None
    win.paste_selected()
    areas = [o for o in win.objects if o.obj_type == "System Boundary"]
    assert len(areas) == 1
    wps = [o for o in win.objects if o.obj_type == "Work Product"]
    assert len(wps) == 1
    new_area = areas[0]
    new_wp = wps[0]
    assert new_wp.properties.get("parent") == str(new_area.obj_id)


def test_cross_diagram_paste_creates_process_area():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    app = types.SimpleNamespace(
        diagram_clipboard=None,
        diagram_clipboard_type=None,
        diagram_clipboard_parent_name=None,
    )
    win1 = _setup_window(repo=repo, app=app)
    win2 = _setup_window(repo=repo, app=app)
    area = win1._place_process_area("Risk Assessment", 0.0, 0.0)
    wp = win1._place_work_product("Risk Assessment", 10.0, 0.0, area=area)
    win1.selected_obj = wp
    win1.copy_selected()
    win2.selected_obj = None
    win2.paste_selected()
    areas = [o for o in win2.objects if o.obj_type == "System Boundary"]
    assert len(areas) == 1
    wps = [o for o in win2.objects if o.obj_type == "Work Product"]
    assert len(wps) == 1
    assert wps[0].properties.get("parent") == str(areas[0].obj_id)
    assert areas[0].properties.get("name") == "Risk Assessment"
