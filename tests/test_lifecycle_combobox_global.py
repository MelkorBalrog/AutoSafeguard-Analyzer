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
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from AutoML import AutoMLApp


def test_global_phase_included_when_root_diagram_exists():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1")]
    toolbox.create_diagram("RootDiag")
    app = AutoMLApp.__new__(AutoMLApp)
    app.safety_mgmt_toolbox = toolbox
    captured = {}

    class DummyCB:
        def configure(self, **kwargs):
            captured.update(kwargs)

    app.lifecycle_cb = DummyCB()
    app.lifecycle_var = types.SimpleNamespace(set=lambda _v: None)
    app.update_lifecycle_cb()
    assert "GLOBAL" in captured.get("values", [])
