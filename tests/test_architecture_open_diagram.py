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

from gui.architecture import ArchitectureManagerDialog
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def test_open_diagram_uses_diag_id():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Use Case Diagram", name="UC")

    called = []

    def fake_open_arch_window(arg):
        called.append(arg)

    app = types.SimpleNamespace(
        window_controllers=types.SimpleNamespace(open_arch_window=fake_open_arch_window),
        diagram_tabs={},
    )

    explorer = ArchitectureManagerDialog.__new__(ArchitectureManagerDialog)
    explorer.repo = repo
    explorer.app = app
    explorer.master = None

    explorer.open_diagram(diag.diag_id)

    assert called == [diag.diag_id]
