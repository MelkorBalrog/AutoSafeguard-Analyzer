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
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc


def _make_window(app, doc):
    win = object.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.nodes = {}
    win.id_to_node = {}
    win.edges = []
    win.NODE_RADIUS = 10
    win.canvas = types.SimpleNamespace(delete=lambda *a, **k: None)
    win.drawing_helper = types.SimpleNamespace(_fill_gradient_circle=lambda *a, **k: [])
    win._draw_node = lambda *a, **k: None
    win._draw_edge = lambda *a, **k: None
    win._place_table = lambda *a, **k: None
    win._update_scroll_region = lambda: None
    return win


def test_cbn_copy_paste_shared_properties_independent_position():
    doc1 = CausalBayesianNetworkDoc(name="d1")
    doc1.network.add_node("A", cpd=0.5)
    doc1.network.add_node("B", parents=["A"], cpd={(True,): 0.5, (False,): 0.1})
    doc1.positions["B"] = [(0, 0)]
    doc1.types["B"] = "variable"
    app = types.SimpleNamespace(
        active_cbn=doc1,
        cbn_docs=[doc1],
        diagram_clipboard=None,
        diagram_clipboard_type=None,
    )

    win1 = _make_window(app, doc1)

    snap1 = win1._clone_node_strategy1(("B", 0))
    snap2 = win1._clone_node_strategy2(("B", 0))
    snap3 = win1._clone_node_strategy3(("B", 0))
    snap4 = win1._clone_node_strategy4(("B", 0))
    assert snap1 == snap2 == snap3 == snap4 == (doc1, "B", 0)

    win1.selected_node = ("B", 0)
    win1.copy_selected()
    assert app.diagram_clipboard == (doc1, "B", 0)
    assert app.diagram_clipboard_type == "Causal Bayesian Network"

    doc2 = CausalBayesianNetworkDoc(name="d2")
    app.cbn_docs.append(doc2)
    app.active_cbn = doc2
    win2 = _make_window(app, doc2)

    for strat in (
        win2._reconstruct_node_strategy1,
        win2._reconstruct_node_strategy2,
        win2._reconstruct_node_strategy3,
        win2._reconstruct_node_strategy4,
    ):
        name, idx = strat((doc1, "B", 0), doc2)
        assert name == "B"
        assert doc2.network.cpds["B"] is doc1.network.cpds["B"]
        assert doc2.positions["B"][idx] != doc1.positions["B"][0]

    win2.paste_selected()
    assert "B" in doc2.network.nodes
    assert doc2.network.cpds["B"] is doc1.network.cpds["B"]
    assert doc2.positions["B"][0] == (20, 20)

    doc2.positions["B"][0] = (50, 60)
    assert doc1.positions["B"][0] == (0, 0)

    doc2.types["B"] = "Triggering Condition"
    assert doc1.types["B"] == "Triggering Condition"


def test_cbn_same_diagram_clone_independent_position():
    doc = CausalBayesianNetworkDoc(name="d")
    doc.network.add_node("A", cpd=0.5)
    doc.positions["A"] = [(0, 0)]
    doc.types["A"] = "variable"
    app = types.SimpleNamespace(
        active_cbn=doc,
        cbn_docs=[doc],
        diagram_clipboard=None,
        diagram_clipboard_type=None,
    )
    win = _make_window(app, doc)
    win.selected_node = ("A", 0)
    win.copy_selected()
    win.paste_selected()
    assert len(doc.positions["A"]) == 2
    assert doc.positions["A"][1] != doc.positions["A"][0]
    doc.positions["A"][1] = (50, 60)
    assert doc.positions["A"][0] == (0, 0)
    # data shared
    doc.network.cpds["A"] = 0.3
    assert doc.network.cpds["A"] == 0.3
