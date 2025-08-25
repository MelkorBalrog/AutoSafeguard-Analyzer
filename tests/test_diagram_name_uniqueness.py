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

from tkinter import simpledialog

from gui.gsn_explorer import GSNExplorer
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from mainappsrc.models.gsn import GSNNode, GSNDiagram


def test_unique_gsn_diagram_names(monkeypatch):
    app = types.SimpleNamespace(gsn_diagrams=[], gsn_modules=[])
    root = GSNNode("A", "Goal")
    app.gsn_diagrams.append(GSNDiagram(root))
    explorer = GSNExplorer.__new__(GSNExplorer)
    explorer.app = app
    explorer.tree = types.SimpleNamespace(selection=lambda: ())
    explorer.item_map = {}
    explorer.populate = lambda: None

    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "A")

    explorer.new_diagram()
    assert len(app.gsn_diagrams) == 1


def test_unique_cbn_doc_names(monkeypatch):
    app = types.SimpleNamespace(cbn_docs=[CausalBayesianNetworkDoc(name="A")])
    win = CausalBayesianNetworkWindow.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.refresh_docs = lambda: None
    win.doc_var = types.SimpleNamespace(set=lambda v: None)

    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "A")

    win.new_doc()
    assert len(app.cbn_docs) == 1

