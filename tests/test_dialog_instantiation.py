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
