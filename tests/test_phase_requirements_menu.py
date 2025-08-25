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
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow
from analysis.safety_management import SafetyManagementToolbox


class DummyMenu:
    """Minimal stand-in for ``tk.Menu`` used in tests.

    The real Tk menu cannot be created in the test environment because it
    requires a display.  This dummy object only records commands registered via
    :meth:`add_command` so we can invoke them directly.
    """

    def __init__(self):
        self.commands = []

    def delete(self, _start, _end):  # pragma: no cover - simply satisfies API
        pass

    def add_command(self, label, command):
        self.commands.append((label, command))

    def add_separator(self):  # pragma: no cover - not needed for test
        pass


def test_phase_menu_binds_correct_phase():
    toolbox = SafetyManagementToolbox()
    toolbox.add_module("Phase1")
    toolbox.add_module("Phase2")

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.phase_menu = DummyMenu()

    called = []
    win.generate_phase_requirements = lambda phase: called.append(phase)

    win._refresh_phase_menu()

    # The first entries correspond to the lifecycle phases in alphabetical order
    for label, cmd in win.phase_menu.commands:
        if label == "Lifecycle":
            continue
        called.clear()
        cmd()
        assert called == [label]
