import types

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sysml.sysml_repository import SysMLRepository
from gui.stpa_window import StpaWindow
from gui.threat_window import ThreatWindow


class DummyWidget:
    def __init__(self, *a, textvariable=None, values=None, state=None, **k):
        self.textvariable = textvariable
        self.configured = {"values": values}

    def grid(self, *a, **k):
        pass

    def pack(self, *a, **k):
        pass

    def configure(self, **k):
        self.configured.update(k)


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def set(self, v):
        self._value = v


# ---------------------------------------------------------------------------
# STPA dialog
# ---------------------------------------------------------------------------

def test_stpa_dialog_respects_governance(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Control Flow Diagram", name="CFD1")
    repo.create_diagram("Control Flow Diagram", name="CFD2")

    combo_calls = []

    def combo_stub(*a, **k):
        cb = DummyWidget(*a, **k)
        combo_calls.append(cb)
        return cb

    monkeypatch.setattr("gui.stpa_window.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.stpa_window.ttk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ttk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.tk.StringVar", lambda value="": DummyVar(value))

    class Toolbox:
        def __init__(self, allowed, visible):
            self.allowed = allowed
            self.visible = visible

        def analysis_inputs(self, target, **kwargs):
            return self.allowed

        def document_visible(self, analysis, name):
            return name in self.visible

    app = types.SimpleNamespace(safety_mgmt_toolbox=Toolbox(set(), set()))

    dlg = StpaWindow.NewStpaDialog.__new__(StpaWindow.NewStpaDialog)
    dlg.app = app
    dlg.body(master=DummyWidget())
    assert combo_calls[0].configured["values"] == []

    combo_calls.clear()
    app.safety_mgmt_toolbox.allowed = {"Architecture Diagram"}
    app.safety_mgmt_toolbox.visible = {"CFD1"}

    dlg = StpaWindow.NewStpaDialog.__new__(StpaWindow.NewStpaDialog)
    dlg.app = app
    dlg.body(master=DummyWidget())
    assert combo_calls[0].configured["values"] == ["CFD1 : CFD"]


# ---------------------------------------------------------------------------
# Threat Analysis dialog
# ---------------------------------------------------------------------------

def test_threat_dialog_respects_governance(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Internal Block Diagram", name="IBD1")
    repo.create_diagram("Internal Block Diagram", name="IBD2")

    combo_calls = []

    def combo_stub(*a, **k):
        cb = DummyWidget(*a, **k)
        combo_calls.append(cb)
        return cb

    monkeypatch.setattr("gui.threat_window.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.threat_window.ttk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.threat_window.ttk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.threat_window.tk.StringVar", lambda value="": DummyVar(value))

    class Toolbox:
        def __init__(self, allowed, visible):
            self.allowed = allowed
            self.visible = visible

        def analysis_inputs(self, target, **kwargs):
            return self.allowed

        def document_visible(self, analysis, name):
            return name in self.visible

    app = types.SimpleNamespace(safety_mgmt_toolbox=Toolbox(set(), set()))

    dlg = ThreatWindow.NewThreatDialog.__new__(ThreatWindow.NewThreatDialog)
    dlg.app = app
    dlg.body(master=DummyWidget())
    assert combo_calls[0].configured["values"] == []

    combo_calls.clear()
    app.safety_mgmt_toolbox.allowed = {"Architecture Diagram"}
    app.safety_mgmt_toolbox.visible = {"IBD1"}

    dlg = ThreatWindow.NewThreatDialog.__new__(ThreatWindow.NewThreatDialog)
    dlg.app = app
    dlg.body(master=DummyWidget())
    assert combo_calls[0].configured["values"] == ["IBD1 : IBD"]
