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

from analysis.models import HaraDoc
from gui.toolboxes import RiskAssessmentWindow


def test_edit_doc_updates_selections(monkeypatch):
    doc = HaraDoc(
        "RA1",
        ["HZ1"],
        [],
        False,
        "draft",
        stpa="STPA1",
        threat="TA1",
        fi2tc="FI1",
        tc2fi="TC1",
    )
    app = types.SimpleNamespace(
        active_hara=doc,
        hara_docs=[doc],
        update_views=lambda: None,
    )

    window = RiskAssessmentWindow.__new__(RiskAssessmentWindow)
    window.app = app
    window.refresh_docs = lambda: None
    window.refresh = lambda: None

    class DummyDialog:
        def __init__(self, *a, **k):
            self.result = ("HZ2", "STPA2", "TA2", "FI2", "TC2")

    monkeypatch.setattr(RiskAssessmentWindow, "EditAssessmentDialog", DummyDialog)

    window.edit_doc()

    assert doc.hazops == ["HZ2"]
    assert doc.stpa == "STPA2"
    assert doc.threat == "TA2"
    assert doc.fi2tc == "FI2"
    assert doc.tc2fi == "TC2"
