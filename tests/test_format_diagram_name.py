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

from gui.architecture import format_diagram_name
from mainappsrc.models.sysml.sysml_repository import SysMLDiagram


def test_format_diagram_name_adds_abbreviation():
    diag = SysMLDiagram("d1", "Control Flow Diagram", name="Diag")
    assert format_diagram_name(diag) == "Diag : CFD"


def test_format_diagram_name_ibd():
    diag = SysMLDiagram("d2", "Internal Block Diagram", name="Struct")
    assert format_diagram_name(diag) == "Struct : IBD"


def test_format_diagram_name_does_not_duplicate():
    diag = SysMLDiagram("d3", "Control Flow Diagram", name="Diag : CFD")
    assert format_diagram_name(diag) == "Diag : CFD"

