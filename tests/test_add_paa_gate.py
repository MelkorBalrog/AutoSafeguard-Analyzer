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

"""Verify that gates can be added in Prototype Assurance Analysis diagrams."""

import sys
import pathlib
import types

repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

import AutoML

AutoMLApp = AutoML.AutoMLApp
FaultTreeNode = AutoML.FaultTreeNode


def _make_app(root):
    app = AutoMLApp.__new__(AutoMLApp)
    app.root_node = root
    app.top_events = [root]
    app.selected_node = root
    app.analysis_tree = types.SimpleNamespace(selection=lambda: ())
    app.update_views = lambda: None
    app.find_node_by_id_all = lambda uid: root if uid == root.unique_id else None
    app.push_undo_state = lambda: None
    app.diagram_mode = "PAA"
    return app


def test_add_gate_in_paa(monkeypatch):
    root = FaultTreeNode("Root", "TOP EVENT")
    app = _make_app(root)

    warnings = []
    monkeypatch.setattr(
        AutoML.messagebox, "showwarning", lambda *a, **k: warnings.append(a)
    )

    app.add_node_of_type("Gate")

    assert not warnings
    assert len(root.children) == 1
    assert root.children[0].node_type.upper() == "GATE"
