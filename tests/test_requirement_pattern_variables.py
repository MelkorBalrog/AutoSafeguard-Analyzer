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

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram, GeneratedRequirement


def test_requirement_pattern_variables_used():
    diag = GovernanceDiagram()
    diag.add_task("DB", node_type="AI Database")
    diag.add_task("Acquire", node_type="Data acquisition")
    diag.add_relationship("DB", "Acquire", conn_type="Acquisition")
    reqs = [r for r in diag.generate_requirements() if isinstance(r, GeneratedRequirement)]
    pattern_req = next((r for r in reqs if r.variables), None)
    assert pattern_req is not None
    assert "acceptance_criteria" in pattern_req.variables
