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
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule


def test_display_name_and_phase_rename_propagation():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    tb = SafetyManagementToolbox()
    tb.modules = [GovernanceModule(name="P1")]
    tb.set_active_module("P1")
    elem = repo.create_element("Block", name="E1")
    diag = repo.create_diagram("Use Case Diagram", name="D1")
    tb.doc_phases = {"HAZOP": {"HZ1": "P1"}}
    assert elem.display_name() == "E1 (P1)"
    assert diag.display_name() == "D1 : UCD (P1)"
    tb.rename_module("P1", "NP")
    assert elem.phase == "NP"
    assert diag.phase == "NP"
    assert elem.display_name() == "E1 (NP)"
    assert diag.display_name() == "D1 : UCD (NP)"
    assert tb.doc_phases["HAZOP"]["HZ1"] == "NP"


def test_phase_freezes_after_work_product():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    tb = SafetyManagementToolbox()
    diag_id = tb.create_diagram("Gov")
    tb.modules = [GovernanceModule(name="P1", diagrams=["Gov"])]
    tb.set_active_module("P1")
    tb.register_created_work_product("HAZOP", "HZ1")
    assert "P1" in tb.frozen_modules
    assert "Gov" in tb.frozen_diagrams
    assert repo.diagram_read_only(diag_id)
    tb.rename_module("P1", "New")
    assert tb.list_modules() == ["P1", "GLOBAL"]
    tb.rename_diagram("Gov", "Other")
    assert "Gov" in tb.diagrams
