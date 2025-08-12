import types
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis.models import (
    HazopDoc,
    HazopEntry,
    HaraDoc,
    HaraEntry,
    StpaDoc,
    StpaEntry,
    ThreatDoc,
    ThreatEntry,
    FunctionThreat,
    DamageScenario,
    ThreatScenario,
    AttackPath,
)
from gui.toolboxes import RiskAssessmentWindow


def test_row_dialog_filters_stpa_and_threat(monkeypatch):
    """Only selected STPA UCAs and threat scenarios should appear."""

    # --- Analysis documents ---
    hazop = HazopDoc(
        "HZ1",
        [
            HazopEntry(
                "f",
                "HZ_MALF",
                "",
                "",
                "",
                "haz",
                True,
                "",
                False,
                "",
            )
        ],
    )
    stpa_sel = StpaDoc("STPA1", "", [StpaEntry("", "UCA1", "", "", "", [])])
    stpa_other = StpaDoc("STPA2", "", [StpaEntry("", "UCA_OTHER", "", "", "", [])])

    threat_sel = ThreatDoc(
        "TA1",
        [
            ThreatEntry(
                "asset",
                [
                    FunctionThreat(
                        "func",
                        [
                            DamageScenario(
                                "damage",
                                threats=[
                                    ThreatScenario(
                                        "S",
                                        "TS1",
                                        [AttackPath("p")],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )
    threat_other = ThreatDoc(
        "TA2",
        [
            ThreatEntry(
                "asset",
                [
                    FunctionThreat(
                        "func",
                        [
                            DamageScenario(
                                "damage",
                                threats=[
                                    ThreatScenario(
                                        "S",
                                        "TS_OTHER",
                                        [AttackPath("p")],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )

    hara = HaraDoc(
        "RA1",
        ["HZ1"],
        [],
        False,
        "draft",
        stpa="STPA1",
        threat="TA1",
    )

    app = types.SimpleNamespace(
        active_hara=hara,
        hazop_docs=[hazop],
        stpa_docs=[stpa_sel, stpa_other],
        threat_docs=[threat_sel, threat_other],
        top_events=[],
        hazard_severity={},
        get_all_scenario_names=lambda: [],
        get_scenario_exposure=lambda scen: 1,
        sync_cyber_risk_to_goals=lambda: None,
        cybersecurity_goals=[],
    )

    def get_hazop_by_name(name):
        return hazop if name == "HZ1" else None

    app.get_hazop_by_name = get_hazop_by_name

    # --- Stub tkinter widgets ---
    class DummyWidget:
        def __init__(self, *a, textvariable=None, values=None, **k):
            self.textvariable = textvariable
            self.configured = {"values": values}

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

        config = configure

        def add(self, *a, **k):
            pass

        def after(self, *a, **k):
            pass

        def delete(self, *a, **k):
            pass

    class DummyText(DummyWidget):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.content = ""

        def insert(self, index, text):
            self.content += text

        def get(self, *a, **k):
            return self.content

    class DummyCombobox(DummyWidget):
        def __init__(self, *a, textvariable=None, values=None, state=None, **k):
            super().__init__(*a, textvariable=textvariable, values=values, **k)
            self.state = state

    class DummyNotebook(DummyWidget):
        pass

    class DummyVar:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, v):
            self._value = v

        def trace_add(self, *a, **k):
            pass

    combo_calls = []

    def combo_stub(*a, **k):
        cb = DummyCombobox(*a, **k)
        combo_calls.append(cb)
        return cb

    monkeypatch.setattr("gui.toolboxes.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.toolboxes.ttk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.toolboxes.ttk.Frame", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.toolboxes.ttk.Button", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.toolboxes.ttk.Notebook", lambda *a, **k: DummyNotebook())
    monkeypatch.setattr("gui.toolboxes.tk.Text", DummyText)
    monkeypatch.setattr("gui.toolboxes.tk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.toolboxes.tk.StringVar", lambda value="": DummyVar(value))

    dlg = RiskAssessmentWindow.RowDialog.__new__(RiskAssessmentWindow.RowDialog)
    dlg.app = app
    dlg.row = HaraEntry("", "", "", 1, "", 1, "", 1, "", "QM", "")
    dlg.body(master=DummyWidget())

    mal_values = None
    threat_values = None
    for cb in combo_calls:
        if cb.textvariable is getattr(dlg, "mal_var", None):
            mal_values = cb.configured["values"]
        if cb.textvariable is getattr(dlg, "threat_var", None):
            threat_values = cb.configured["values"]

    assert mal_values == ["HZ_MALF", "UCA1"]
    assert threat_values == ["TS1"]

