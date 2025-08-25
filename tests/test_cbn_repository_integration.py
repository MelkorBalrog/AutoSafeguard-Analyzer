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

import os
import sys
import types
from unittest import mock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from tests.test_causal_bayesian_ui import _setup_window


def _prep_window(tool):
    win, doc = _setup_window()
    win.current_tool = tool
    win.app.triggering_conditions = []
    win.app.functional_insufficiencies = []

    def add_tc(name):
        if name and all(name.lower() != n.lower() for n in win.app.triggering_conditions):
            win.app.triggering_conditions.append(name)

    def add_fi(name):
        if name and all(name.lower() != n.lower() for n in win.app.functional_insufficiencies):
            win.app.functional_insufficiencies.append(name)

    win.app.add_triggering_condition = add_tc
    win.app.add_functional_insufficiency = add_fi
    win.select_tool = lambda t: None
    return win


def test_new_triggering_condition_creates_repo_entry():
    win = _prep_window("Triggering Condition")
    event = types.SimpleNamespace(x=0, y=0)
    with mock.patch("gui.causal_bayesian_network_window.simpledialog.askstring", return_value="TC1"):
        CausalBayesianNetworkWindow.on_click(win, event)
    assert "TC1" in win.app.triggering_conditions


def test_new_functional_insufficiency_creates_repo_entry():
    win = _prep_window("Functional Insufficiency")
    event = types.SimpleNamespace(x=0, y=0)
    with mock.patch("gui.causal_bayesian_network_window.simpledialog.askstring", return_value="FI1"):
        CausalBayesianNetworkWindow.on_click(win, event)
    assert "FI1" in win.app.functional_insufficiencies
