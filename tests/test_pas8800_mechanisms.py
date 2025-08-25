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

import sys
import types
from analysis.mechanisms import PAS_8800_MECHANISMS
from analysis.models import MechanismLibrary

def _stub_review_toolbox():
    """Provide a lightweight stub for gui.review_toolbox.

    The real module depends on Pillow which isn't available in the test
    environment.  The application only requires the names of several classes
    when importing, so simple placeholders are sufficient."""
    rt = types.ModuleType("gui.review_toolbox")
    placeholders = [
        "ReviewToolbox",
        "ReviewData",
        "ReviewParticipant",
        "ReviewComment",
        "ParticipantDialog",
        "EmailConfigDialog",
        "ReviewScopeDialog",
        "UserSelectDialog",
        "ReviewDocumentDialog",
        "VersionCompareDialog",
    ]
    for name in placeholders:
        setattr(rt, name, type(name, (), {}))
    sys.modules.setdefault("gui.review_toolbox", rt)


def test_pas8800_contains_fault_aware_training():
    names = [m.name for m in PAS_8800_MECHANISMS]
    assert "Fault-aware training" in names


def test_pas8800_contains_new_diagnostics():
    names = [m.name for m in PAS_8800_MECHANISMS]
    expected = [
        "Bayesian inference",
        "Monte Carlo dropout",
        "Data distillation",
        "Auto data labeling and annotation",
    ]
    for mech in expected:
        assert mech in names


def test_pas8800_library_non_empty():
    lib = MechanismLibrary("PAS 8800", PAS_8800_MECHANISMS.copy())
    assert len(lib.mechanisms) >= 30


def test_default_mechanisms_include_pas8800():
    _stub_review_toolbox()
    from AutoML import AutoMLApp

    class Dummy:
        def __init__(self):
            self.mechanism_libraries = []
            self.selected_mechanism_libraries = []

    Dummy.load_default_mechanisms = AutoMLApp.load_default_mechanisms
    obj = Dummy()
    obj.load_default_mechanisms()

    names = [lib.name for lib in obj.mechanism_libraries]
    selected = [lib.name for lib in obj.selected_mechanism_libraries]
    assert "PAS 8800" in names
    assert "PAS 8800" in selected
