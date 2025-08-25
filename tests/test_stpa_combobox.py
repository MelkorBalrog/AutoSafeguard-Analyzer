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
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis.models import StpaEntry
from gui.stpa_window import StpaWindow


def test_row_dialog_populates_control_actions(monkeypatch):
    """The control action combo box should list actions and preselect one."""

    app = types.SimpleNamespace()
    parent = StpaWindow.__new__(StpaWindow)
    parent.app = app
    parent._get_control_actions = lambda: ["Act"]

    # ------------------------------------------------------------------
    # Stub tkinter widgets so the dialog can be created without a display
    # ------------------------------------------------------------------
    class DummyWidget:
        def __init__(self, *args, **kwargs):
            self.configured = {}

        def grid(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

        def insert(self, *a, **k):
            pass

        def bind(self, *a, **k):
            pass

        def configure(self, **k):
            self.configured.update(k)

    class DummyCombobox(DummyWidget):
        def __init__(self, *a, textvariable=None, state=None, **k):
            super().__init__(*a, **k)
            self.textvariable = textvariable
            self.state = state

    combo_holder = {}

    def combo_stub(*a, **k):
        cb = DummyCombobox(*a, **k)
        combo_holder["cb"] = cb
        return cb

    monkeypatch.setattr("gui.stpa_window.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.stpa_window.ttk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ttk.Frame", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ttk.Button", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.TranslucidButton", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.tk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.tk.Listbox", lambda *a, **k: DummyWidget())

    class DummyVar:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, v):
            self._value = v

    monkeypatch.setattr("gui.stpa_window.tk.StringVar", lambda value="": DummyVar(value))

    dlg = StpaWindow.RowDialog.__new__(StpaWindow.RowDialog)
    dlg.parent = parent
    dlg.app = app
    dlg.row = StpaEntry("", "", "", "", "", [])

    dlg.body(master=DummyWidget())

    cb = combo_holder["cb"]
    assert cb.configured["values"] == ["Act"]
    assert dlg.action_var.get() == "Act"


def test_row_dialog_control_action_tooltip(monkeypatch):
    """The combo box tooltip should show the full selected action."""

    app = types.SimpleNamespace()
    parent = StpaWindow.__new__(StpaWindow)
    parent.app = app
    parent._get_control_actions = lambda: ["Act1", "Act2"]

    class DummyWidget:
        def __init__(self, *args, **kwargs):
            self.configured = {}
            self.bindings = {}

        def grid(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

        def insert(self, *a, **k):
            pass

        def bind(self, event, func):
            self.bindings[event] = func

        def configure(self, **k):
            self.configured.update(k)

        def after(self, *a, **k):
            pass

    class DummyCombobox(DummyWidget):
        def __init__(self, *a, textvariable=None, state=None, **k):
            super().__init__(*a, **k)
            self.textvariable = textvariable
            self.state = state

    combo_holder = {}

    def combo_stub(*a, **k):
        cb = DummyCombobox(*a, **k)
        combo_holder["cb"] = cb
        return cb

    tooltip_holder = {}

    class DummyToolTip:
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            tooltip_holder["tip"] = self

    monkeypatch.setattr("gui.stpa_window.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.stpa_window.ttk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ttk.Frame", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ttk.Button", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.TranslucidButton", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.tk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.tk.Listbox", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ToolTip", DummyToolTip)

    class DummyVar:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, v):
            self._value = v

    monkeypatch.setattr("gui.stpa_window.tk.StringVar", lambda value="": DummyVar(value))

    dlg = StpaWindow.RowDialog.__new__(StpaWindow.RowDialog)
    dlg.parent = parent
    dlg.app = app
    dlg.row = StpaEntry("", "", "", "", "", [])

    dlg.body(master=DummyWidget())

    tip = tooltip_holder["tip"]
    assert tip.text == "Act1"
    cb = combo_holder["cb"]
    dlg.action_var.set("Act2")
    cb.bindings["<<ComboboxSelected>>"](None)
    assert tip.text == "Act2"


