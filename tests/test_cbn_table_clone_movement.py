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

from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


class DummyFrame:
    def __init__(self, w=20, h=10):
        self.w = w
        self.h = h

    def winfo_reqwidth(self):
        return self.w

    def winfo_reqheight(self):
        return self.h

    def update_idletasks(self):
        pass

    def destroy(self):
        pass


class DummyCanvas:
    def __init__(self):
        self.coords_map = {}
        self.next_id = 1

    def create_oval(self, *a, **k):
        i = self.next_id
        self.next_id += 1
        return i

    def create_text(self, *a, **k):
        i = self.next_id
        self.next_id += 1
        return i

    def create_window(self, *a, **k):
        i = self.next_id
        self.next_id += 1
        self.coords_map[i] = (0, 0)
        return i

    def itemconfigure(self, *a, **k):
        pass

    def coords(self, win, *args):
        if args:
            self.coords_map[win] = (args[0], args[1])
        return self.coords_map.get(win, (0, 0))

    def delete(self, *a, **k):
        pass

    def move(self, win, dx, dy):
        x, y = self.coords_map.get(win, (0, 0))
        self.coords_map[win] = (x + dx, y + dy)

    def find_withtag(self, tag):
        return []


def test_cbn_probability_tables_follow_each_clone():
    doc = CausalBayesianNetworkDoc(name="d")
    doc.network.add_node("A", cpd=0.5)
    doc.positions["A"] = [(0, 0)]
    doc.types["A"] = "variable"
    app = types.SimpleNamespace(active_cbn=doc, cbn_docs=[doc])

    win = object.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.NODE_RADIUS = 10
    win.nodes = {}
    win.id_to_node = {}
    win.edges = []
    win.tables = {}
    win.canvas = DummyCanvas()
    win.drawing_helper = types.SimpleNamespace(_fill_gradient_circle=lambda *a, **k: [])
    win._update_scroll_region = lambda: None

    def _place_table_stub(name, idx):
        frame = DummyFrame()
        win_id = win.canvas.create_window(0, 0)
        tables = win.tables.setdefault(name, [])
        while len(tables) <= idx:
            tables.append(None)
        tables[idx] = (win_id, frame, None)
        x, y = doc.positions.get(name, [(0, 0)])[idx]
        win._position_table(name, idx, x, y)

    win._place_table = _place_table_stub
    win._update_table = lambda *a, **k: None

    win._draw_node("A", 0, 0, "variable", idx=0)
    doc.positions["A"].append((40, 50))
    win._draw_node("A", 40, 50, "variable", idx=1)

    t0 = win.tables["A"][0][0]
    t1 = win.tables["A"][1][0]
    c0 = win.canvas.coords(t0)
    c1 = win.canvas.coords(t1)

    win._position_table("A", 0, 100, 100)
    assert win.canvas.coords(t0) != c0
    assert win.canvas.coords(t1) == c1

    frozen = win.canvas.coords(t0)
    win._position_table("A", 1, 200, 200)
    assert win.canvas.coords(t1) != c1
    assert win.canvas.coords(t0) == frozen
