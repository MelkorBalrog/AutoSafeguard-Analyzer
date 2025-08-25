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
import gui.safety_case_explorer as safety_case_explorer


def test_open_case_uses_app_tab(monkeypatch):
    case = types.SimpleNamespace(name="MyCase", solutions=[])
    explorer = safety_case_explorer.SafetyCaseExplorer.__new__(
        safety_case_explorer.SafetyCaseExplorer
    )
    explorer.tree = types.SimpleNamespace(selection=lambda: ("i1",))
    explorer.item_map = {"i1": ("case", case)}
    called = {}

    class DummyTab:
        def __init__(self):
            self.packed = False
        def pack(self, **kwargs):
            self.packed = True

    def fake_new_tab(title):
        called["title"] = title
        return DummyTab()

    explorer.app = types.SimpleNamespace(_new_tab=fake_new_tab)

    class DummyTable:
        def __init__(self, master, case, app=None):
            called["master"] = master
            called["case"] = case
        def pack(self, **kwargs):
            called["packed"] = True

    monkeypatch.setattr(safety_case_explorer, "SafetyCaseTable", DummyTable)
    monkeypatch.setattr(
        safety_case_explorer.tk,
        "Toplevel",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Toplevel called")),
    )

    safety_case_explorer.SafetyCaseExplorer.open_item(explorer)

    assert called["title"] == "Safety & Security Report: MyCase"
    assert called["master"].packed is False
    assert called["case"] is case
    assert called.get("packed") is True
