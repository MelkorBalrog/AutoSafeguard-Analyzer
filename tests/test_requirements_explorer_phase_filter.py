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
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.toolboxes import RequirementsExplorerWindow
from analysis.models import global_requirements


class DummyVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


class DummyTree:
    def __init__(self):
        self.data = []

    def delete(self, *items):
        self.data = []

    def get_children(self):  # pragma: no cover - structure only
        return list(range(len(self.data)))

    def insert(self, _parent, _index, values=()):
        self.data.append(values)


def _make_window(active_phase):
    app = types.SimpleNamespace(
        safety_mgmt_toolbox=types.SimpleNamespace(active_module=active_phase)
    )
    win = RequirementsExplorerWindow.__new__(RequirementsExplorerWindow)
    win.app = app
    win.tree = DummyTree()
    win.query_var = DummyVar()
    win.type_var = DummyVar()
    win.asil_var = DummyVar()
    win.status_var = DummyVar()
    return win


def test_explorer_filters_by_active_phase():
    global_requirements.clear()
    global_requirements.update(
        {
            "R1": {"text": "Req1", "req_type": "organizational", "phase": "P1"},
            "R2": {"text": "Req2", "req_type": "organizational", "phase": None},
            "R3": {"text": "Req3", "req_type": "organizational", "phase": "P2"},
        }
    )

    win = _make_window("P1")
    win.refresh()
    assert [v[0] for v in win.tree.data] == ["R1", "R2"]

    win.app.safety_mgmt_toolbox.active_module = "P2"
    win.refresh()
    assert [v[0] for v in win.tree.data] == ["R2", "R3"]

    win.app.safety_mgmt_toolbox.active_module = None
    win.refresh()
    assert [v[0] for v in win.tree.data] == ["R1", "R2", "R3"]

