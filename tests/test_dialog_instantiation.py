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


from __future__ import annotations

import types
import tkinter.simpledialog as simpledialog

from gui.dialogs.req_dialog import ReqDialog
from gui.dialogs.fmea_row_dialog import FMEARowDialog
from gui.dialogs.select_base_event_dialog import SelectBaseEventDialog


def _stub_init(self, *args, **kwargs):
    """Stubbed initializer to avoid creating real GUI windows."""
    pass


def test_req_dialog_instantiation(monkeypatch):
    monkeypatch.setattr(simpledialog.Dialog, "__init__", _stub_init)
    dlg = ReqDialog(None, "Add")
    assert isinstance(dlg, ReqDialog)


def test_fmea_row_dialog_instantiation(monkeypatch):
    monkeypatch.setattr(simpledialog.Dialog, "__init__", _stub_init)
    node = types.SimpleNamespace()
    app = types.SimpleNamespace(selected_node=None)
    dlg = FMEARowDialog(None, node, app, [])
    assert isinstance(dlg, FMEARowDialog)


def test_select_base_event_dialog_instantiation(monkeypatch):
    monkeypatch.setattr(simpledialog.Dialog, "__init__", _stub_init)
    events = [types.SimpleNamespace(description="A"), types.SimpleNamespace(description="B")]
    dlg = SelectBaseEventDialog(None, events)
    assert isinstance(dlg, SelectBaseEventDialog)
