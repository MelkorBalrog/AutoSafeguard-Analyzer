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

from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def _setup():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag_id = toolbox.create_diagram("Gov1")
    toolbox.modules = [GovernanceModule("P1", diagrams=["Gov1"])]
    toolbox.diagrams["Gov1"] = diag_id
    toolbox.add_work_product("Gov1", "FMEA", "")
    toolbox.add_work_product("Gov1", "FTA", "")
    return repo, toolbox, diag_id


def test_freeze_after_work_product_blocks_changes():
    repo, toolbox, diag_id = _setup()
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("FMEA", "Doc1")
    mod = toolbox._find_module("P1", toolbox.modules)
    assert mod.frozen
    assert repo.diagrams[diag_id].locked
    toolbox.rename_module("P1", "P1_new")
    assert toolbox.modules[0].name == "P1"
    toolbox.add_work_product("Gov1", "FMEDA", "")
    assert all(wp.analysis != "FMEDA" for wp in toolbox.work_products)
    assert not toolbox.remove_work_product("Gov1", "FTA")
    toolbox.rename_diagram("Gov1", "GovX")
    assert repo.diagrams[diag_id].name == "Gov1"


def test_freeze_on_element_creation_blocks_changes():
    repo, toolbox, diag_id = _setup()
    toolbox.set_active_module("P1")
    repo.create_element("Block", "B1")
    mod = toolbox._find_module("P1", toolbox.modules)
    assert mod.frozen
    toolbox.rename_module("P1", "P1_new")
    assert toolbox.modules[0].name == "P1"
    toolbox.add_work_product("Gov1", "FMEDA", "")
    assert all(wp.analysis != "FMEDA" for wp in toolbox.work_products)
    assert not toolbox.remove_work_product("Gov1", "FTA")
    toolbox.rename_diagram("Gov1", "GovX")
    assert repo.diagrams[diag_id].name == "Gov1"
