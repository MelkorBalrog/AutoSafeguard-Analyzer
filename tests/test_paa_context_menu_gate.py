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
import types

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mainappsrc.core.navigation_selection_input import Navigation_Selection_Input


def test_paa_context_menu_add_gate(monkeypatch):
    labels = []

    class DummyMenu:
        def __init__(self, root, tearoff=0):
            pass

        def add_command(self, label, command=None, accelerator=None):
            labels.append(label)

        def add_separator(self):
            pass

        def tk_popup(self, x, y):  # pragma: no cover - no GUI
            pass

    monkeypatch.setattr(
        "mainappsrc.core.navigation_selection_input.tk.Menu", DummyMenu
    )

    class Node:
        node_type = "Basic Event"
        x = 0
        y = 0
        children = []
        unique_id = 1

    node = Node()

    class Canvas:
        diagram_mode = "PAA"

        def canvasx(self, x):
            return x

        def canvasy(self, y):
            return y

    class App:
        root = None
        canvas = Canvas()
        zoom = 1
        root_node = node
        selected_node = None

        def get_all_nodes(self, root_node):
            return [node]

        # Placeholder callbacks referenced by context menu
        edit_selected = remove_connection = delete_node_and_subtree = (
            remove_node
        ) = copy_node = cut_node = paste_node = edit_description = edit_rationale = (
            edit_value
        ) = edit_gate_type = edit_severity = edit_controllability = (
            edit_page_flag
        ) = add_node_of_type = lambda *a, **k: None
        user_manager = types.SimpleNamespace(edit_user_name=lambda: None)

    nsi = Navigation_Selection_Input.__new__(Navigation_Selection_Input)
    nsi.app = App()
    event = types.SimpleNamespace(x=0, y=0, x_root=0, y_root=0)
    nsi.show_context_menu(event)

    assert "Add Gate" in labels
