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

from gui.safety_management_toolbox import SafetyManagementWindow
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements


class DummyGov:
    def __init__(self, reqs):
        self._reqs = reqs

    def generate_requirements(self):
        return self._reqs


def _setup_window(monkeypatch):
    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    toolbox = types.SimpleNamespace(
        diagrams={"D": "id1"},
        diagrams_for_module=lambda phase: {"D"},
        list_modules=lambda: ["Phase1"],
        module_for_diagram=lambda name: "Phase1",
        list_diagrams=lambda: {"D"},
    )
    win.toolbox = toolbox
    win.app = types.SimpleNamespace()
    win._display_requirements = (
        lambda *args, **kwargs: types.SimpleNamespace(
            refresh_table=lambda ids: None
        )
    )
    monkeypatch.setattr(smt.SysMLRepository, "get_instance", lambda: object())
    return win


def test_existing_requirement_reused(monkeypatch):
    win = _setup_window(monkeypatch)

    monkeypatch.setattr(
        smt.GovernanceDiagram,
        "from_repository",
        lambda repo, diag_id: DummyGov([("Req1", "organizational")]),
    )
    global_requirements.clear()
    win.generate_phase_requirements("Phase1")
    assert len(global_requirements) == 1

    monkeypatch.setattr(
        smt.GovernanceDiagram,
        "from_repository",
        lambda repo, diag_id: DummyGov(
            [("Req1", "organizational"), ("Req2", "organizational")]
        ),
    )
    win.generate_phase_requirements("Phase1")
    texts = [req["text"] for req in global_requirements.values()]
    statuses = {req["text"]: req["status"] for req in global_requirements.values()}
    assert texts.count("Req1") == 1
    assert statuses["Req1"] == "draft"
    assert "Req2" in texts
    assert statuses["Req2"] == "draft"
