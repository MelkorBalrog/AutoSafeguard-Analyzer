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

from gui.architecture import GovernanceDiagramWindow
import gui.architecture as arch


def test_governance_diagram_has_no_select_button(monkeypatch):
    class DummyButton:
        def __init__(self):
            self.config = {}

        def configure(self, **kwargs):
            self.config.update(kwargs)

        def destroy(self):
            self.destroyed = True

    def fake_sysml_init(self, master, title, tools, diagram_id=None, app=None, history=None, relation_tools=None, tool_groups=None):
        self.tool_buttons = {"Select": DummyButton(), "Action": DummyButton()}
        self.toolbox = types.SimpleNamespace()
        self.tools_frame = None
        self.rel_frame = None
        canvas_master = types.SimpleNamespace(pack_forget=lambda: None, pack=lambda **k: None)
        self.canvas = types.SimpleNamespace(master=canvas_master)
        self.repo = types.SimpleNamespace(diagrams={})
        self.diagram_id = "dummy"
        self.refresh_from_repository = lambda *_: None

    monkeypatch.setattr(arch.SysMLDiagramWindow, "__init__", fake_sysml_init)

    win = GovernanceDiagramWindow(None, None)
    assert "Select" not in win.tool_buttons
    assert "Task" in win.tool_buttons
