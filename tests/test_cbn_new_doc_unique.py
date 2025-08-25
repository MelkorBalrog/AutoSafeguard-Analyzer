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
from gui.controls import messagebox
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc


def test_new_doc_rejects_duplicate_name(monkeypatch):
    app = types.SimpleNamespace(cbn_docs=[CausalBayesianNetworkDoc("Existing")])
    win = CausalBayesianNetworkWindow.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.toolbox = None
    win.refresh_docs = lambda: None
    win.doc_var = types.SimpleNamespace(set=lambda *a, **k: None)
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "Existing")
    called = {}
    monkeypatch.setattr(messagebox, "showwarning", lambda *a, **k: called.setdefault("warn", True))
    win.new_doc()
    assert called.get("warn")
    assert len(app.cbn_docs) == 1
