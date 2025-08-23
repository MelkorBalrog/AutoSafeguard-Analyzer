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
