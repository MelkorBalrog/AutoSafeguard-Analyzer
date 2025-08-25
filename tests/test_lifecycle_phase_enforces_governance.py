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

from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

def test_diagram_and_elements_hidden_without_phase():
    repo = SysMLRepository.reset_instance()
    # create diagram and element before any lifecycle phase is active
    diag = repo.create_diagram("Control Flow Diagram", name="CF")
    elem = repo.create_element("Block", name="B1")
    repo.add_element_to_diagram(diag.diag_id, elem.elem_id)
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1"), GovernanceModule("P2")]
    # activate first phase
    toolbox.set_active_module("P1")
    # diagram and element were created without a phase, so they should now be hidden
    assert not repo.diagram_visible(diag.diag_id)
    assert diag.diag_id not in repo.visible_diagrams()
    assert elem.elem_id not in repo.visible_elements()
    # document visibility is also blocked
    assert not toolbox.document_visible("Control Flow Diagram", diag.name)

