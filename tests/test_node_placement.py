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

# Ensure repository root is on path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from mainappsrc.models.fta.fault_tree_node import FaultTreeNode, add_node_of_type


def _make_app(mode: str):
    parent = FaultTreeNode("", "GATE")
    parent.x = 100
    parent.y = 200

    class Canvas:
        diagram_mode = mode

    app = types.SimpleNamespace(
        selected_node=parent,
        canvas=Canvas(),
        diagram_mode=mode,
        push_undo_state=lambda: None,
        update_views=lambda: None,
    )
    return app, parent


def test_new_nodes_appear_below_parent_fta():
    app, parent = _make_app("FTA")
    node = add_node_of_type(app, "Basic Event")
    assert node.y > parent.y


def test_new_nodes_appear_below_parent_cta():
    app, parent = _make_app("CTA")
    node = add_node_of_type(app, "Triggering Condition")
    assert node.y > parent.y


def test_new_nodes_appear_below_parent_paa():
    app, parent = _make_app("PAA")
    node = add_node_of_type(app, "Confidence Level")
    assert node.y > parent.y
