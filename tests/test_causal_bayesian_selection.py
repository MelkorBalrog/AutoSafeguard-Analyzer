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

from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


def test_find_node_strategies_with_scroll():
    offset = 100

    class CanvasStub:
        def canvasx(self, x):
            return x + offset

        def canvasy(self, y):
            return y

        def find_overlapping(self, x1, y1, x2, y2):
            if x1 <= 110 <= x2 and y1 <= 15 <= y2:
                return [1]
            return []

        def find_closest(self, x, y):
            return [1]

        def coords(self, obj_id):
            return [100, 0, 120, 30]

    win = object.__new__(CausalBayesianNetworkWindow)
    win._w = "stub"
    win.canvas = CanvasStub()
    win.id_to_node = {1: ("A", 0)}
    win.nodes = {"A": [(1, None, "fill_A_0")]} 
    win.NODE_RADIUS = 10
    win.app = types.SimpleNamespace(
        active_cbn=types.SimpleNamespace(positions={"A": [(110, 15)]})
    )

    assert win._find_node_strategy1(10, 15) == ("A", 0)
    assert win._find_node_strategy2(10, 15) == ("A", 0)
    assert win._find_node_strategy3(10, 15) == ("A", 0)
    assert win._find_node_strategy4(10, 15) == ("A", 0)
    assert win._find_node(10, 15) == ("A", 0)


def test_on_click_selects_node_and_drag_moves_only_clone():
    doc = types.SimpleNamespace(positions={"A": [(0, 0), (10, 10)]})
    app = types.SimpleNamespace(active_cbn=doc, push_undo_state=lambda: None)

    class CanvasStub:
        def move(self, *args, **kwargs):
            pass

        def coords(self, *args, **kwargs):
            return [0, 0, 0, 0]

    win = object.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.canvas = CanvasStub()
    win.nodes = {"A": [(1, 2, "fill_A_0"), (3, 4, "fill_A_1")]} 
    win.id_to_node = {}
    win.edges = []
    win.NODE_RADIUS = 10
    win._position_table = lambda *a, **k: None
    win._drag_table = lambda *a, **k: None
    win._update_scroll_region = lambda: None
    win._highlight_node = lambda node: setattr(win, "selected_node", node)
    win.selection_rect = None

    win.current_tool = "Select"
    win._find_node = lambda x, y: ("A", 1)
    win.on_click(types.SimpleNamespace(x=10, y=10))
    assert win.selected_node == ("A", 1)

    win.on_drag(types.SimpleNamespace(x=20, y=20))
    assert doc.positions["A"][1] == (20, 20)
    assert doc.positions["A"][0] == (0, 0)


def test_dragging_clone_moves_only_its_fill():
    moves = []

    class CanvasStub:
        def move(self, tag, dx, dy):
            moves.append(tag)

        def coords(self, *args, **kwargs):
            return [0, 0, 0, 0]

    doc = types.SimpleNamespace(positions={"A": [(0, 0), (0, 0)]})
    app = types.SimpleNamespace(active_cbn=doc, push_undo_state=lambda: None)

    win = object.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.canvas = CanvasStub()
    win.nodes = {"A": [(1, 2, "fill_A_0"), (3, 4, "fill_A_1")]}
    win.id_to_node = {}
    win.edges = []
    win.NODE_RADIUS = 10
    win._position_table = lambda *a, **k: None
    win._drag_table = lambda *a, **k: None
    win._update_scroll_region = lambda: None
    win._highlight_node = lambda node: setattr(win, "selected_node", node)
    win.selection_rect = None

    win.current_tool = "Select"
    win._find_node = lambda x, y: ("A", 1)
    win.on_click(types.SimpleNamespace(x=0, y=0))
    win.on_drag(types.SimpleNamespace(x=5, y=5))
    assert moves[0] == "fill_A_1"
