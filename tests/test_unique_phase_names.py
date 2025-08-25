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

from analysis.safety_management import SafetyManagementToolbox
from analysis import safety_management

def test_add_module_enforces_unique_names():
    prev = safety_management.ACTIVE_TOOLBOX
    tb = SafetyManagementToolbox()
    tb.add_module("Phase")
    tb.add_module("Phase")
    parent = tb.add_module("Parent")
    child = tb.add_module("Phase", parent=parent)
    assert [m.name for m in tb.modules] == ["Phase", "Phase_1", "Parent"]
    assert child.name == "Phase_2"
    assert tb.list_modules() == ["Phase", "Phase_1", "Parent", "Phase_2", "GLOBAL"]
    assert len(set(tb.list_modules())) == 5
    safety_management.ACTIVE_TOOLBOX = prev
