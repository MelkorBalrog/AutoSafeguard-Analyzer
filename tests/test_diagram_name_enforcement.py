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

from types import SimpleNamespace
from unittest.mock import patch

from gui.gsn_explorer import GSNExplorer
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


def test_gsn_new_diagram_duplicate_name():
    app = SimpleNamespace(gsn_diagrams=[], gsn_modules=[])
    explorer = GSNExplorer.__new__(GSNExplorer)
    explorer.app = app
    explorer.tree = SimpleNamespace(selection=lambda: [])
    explorer.item_map = {}
    explorer.populate = lambda: None
    with patch("gui.gsn_explorer.simpledialog.askstring", return_value="D"):
        with patch("gui.gsn_explorer.messagebox.showwarning", lambda *a, **k: None):
            explorer.new_diagram()
            assert len(app.gsn_diagrams) == 1
            explorer.new_diagram()
            assert len(app.gsn_diagrams) == 1


def test_cbn_new_doc_duplicate_name():
    app = SimpleNamespace(cbn_docs=[])
    win = CausalBayesianNetworkWindow.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.refresh_docs = lambda: None
    win.doc_var = SimpleNamespace(set=lambda v: None)
    win.select_doc = lambda: None
    with patch("gui.causal_bayesian_network_window.simpledialog.askstring", return_value="A"):
        with patch("gui.causal_bayesian_network_window.messagebox.showwarning", lambda *a, **k: None):
            win.new_doc()
            assert len(app.cbn_docs) == 1
            win.new_doc()
            assert len(app.cbn_docs) == 1

