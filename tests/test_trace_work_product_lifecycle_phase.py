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

from mainappsrc.models.sysml.sysml_repository import SysMLRepository, SysMLDiagram
from gui.architecture import SysMLDiagramWindow, SysMLObject


def test_work_product_to_lifecycle_phase_trace_allowed():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    diag = SysMLDiagram(diag_id="d", diag_type="Governance Diagram")
    repo.diagrams["d"] = diag

    wp = SysMLObject(1, "Work Product", 0, 0, properties={"name": "WP"})
    phase = SysMLObject(2, "Lifecycle Phase", 100, 0, properties={"name": "Phase"})
    diag.objects = [wp, phase]

    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.repo = repo
    win.diagram_id = "d"
    win.connections = []
    win.objects = diag.objects

    valid, msg = SysMLDiagramWindow.validate_connection(win, wp, phase, "Trace")
    assert valid, msg


def test_lifecycle_phase_to_work_product_trace_allowed():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    diag = SysMLDiagram(diag_id="d", diag_type="Governance Diagram")
    repo.diagrams["d"] = diag

    phase = SysMLObject(1, "Lifecycle Phase", 0, 0, properties={"name": "Phase"})
    wp = SysMLObject(2, "Work Product", 100, 0, properties={"name": "WP"})
    diag.objects = [phase, wp]

    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.repo = repo
    win.diagram_id = "d"
    win.connections = []
    win.objects = diag.objects

    valid, msg = SysMLDiagramWindow.validate_connection(win, phase, wp, "Trace")
    assert valid, msg
