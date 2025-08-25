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

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis.safety_management import SafetyManagementToolbox
from analysis.models import global_requirements
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from gui.architecture import link_requirement_to_object


def test_requirement_traces_to_architecture_elements():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    gov = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams["Gov"] = gov.diag_id
    gov.objects = [
        {"obj_id": 1, "obj_type": "Work Product", "x": 0, "y": 0, "properties": {"name": "Architecture Diagram"}},
        {"obj_id": 2, "obj_type": "Work Product", "x": 0, "y": 100, "properties": {"name": "Requirement Specification"}},
    ]
    gov.connections = [{"src": 1, "dst": 2, "conn_type": "Trace"}]
    toolbox.add_work_product("Gov", "Architecture Diagram", "")
    toolbox.add_work_product("Gov", "Requirement Specification", "")

    global_requirements.clear()
    global_requirements["R1"] = {"id": "R1", "req_type": "vehicle", "text": "Req"}

    diag = repo.create_diagram("Activity Diagram", name="Act")
    obj = {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "requirements": []}
    diag.objects.append(obj)

    assert toolbox.can_trace("vehicle", "Architecture Diagram")
    link_requirement_to_object(obj, "R1", diag.diag_id)
    assert diag.diag_id in global_requirements["R1"].get("traces", [])
    assert any(r.get("id") == "R1" for r in obj.get("requirements", []))
