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
from gui.toolboxes import RiskAssessmentWindow


def test_risk_assessment_dialog_hides_unrelated_inputs(monkeypatch):
    """Only work products allowed by governance appear in risk assessment dialogs."""

    # Allow only HAZOP as input to risk assessments
    toolbox = types.SimpleNamespace(analysis_inputs=lambda target: {"HAZOP"})
    app = types.SimpleNamespace(
        hazop_docs=[types.SimpleNamespace(name="HZ1")],
        stpa_docs=[types.SimpleNamespace(name="STPA1")],
        threat_docs=[types.SimpleNamespace(name="TA1")],
        safety_mgmt_toolbox=toolbox,
    )

    class DummyWidget:
        def grid(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

    combos = []

    class DummyCombobox(DummyWidget):
        def __init__(self, *a, textvariable=None, values=None, state=None, **k):
            self.textvariable = textvariable
            self.configured = {"values": values}
            combos.append(self)

        def configure(self, **k):
            self.configured.update(k)

    monkeypatch.setattr("gui.toolboxes.ttk.Combobox", DummyCombobox)
    monkeypatch.setattr("gui.toolboxes.ttk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.toolboxes.ttk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr(
        "gui.toolboxes.tk.StringVar",
        lambda value="": types.SimpleNamespace(get=lambda: value, set=lambda v: None),
    )

    # New assessment dialog filtering
    dlg = RiskAssessmentWindow.NewAssessmentDialog.__new__(
        RiskAssessmentWindow.NewAssessmentDialog
    )
    dlg.app = app
    dlg.body(master=DummyWidget())
    hazop_vals, stpa_vals, fi2tc_vals, tc2fi_vals, threat_vals = [
        cb.configured["values"] for cb in combos
    ]
    assert hazop_vals == ["HZ1"]
    assert stpa_vals == []
    assert fi2tc_vals == []
    assert tc2fi_vals == []
    assert threat_vals == []

    # Edit assessment dialog filtering
    combos.clear()
    doc = types.SimpleNamespace(hazops=["HZ1"], stpa="", threat="", fi2tc="", tc2fi="")
    dlg2 = RiskAssessmentWindow.EditAssessmentDialog.__new__(
        RiskAssessmentWindow.EditAssessmentDialog
    )
    dlg2.app = app
    dlg2.doc = doc
    dlg2.body(master=DummyWidget())
    hazop_vals, stpa_vals, fi2tc_vals, tc2fi_vals, threat_vals = [
        cb.configured["values"] for cb in combos
    ]
    assert hazop_vals == ["HZ1"]
    assert stpa_vals == []
    assert fi2tc_vals == []
    assert tc2fi_vals == []
    assert threat_vals == []
