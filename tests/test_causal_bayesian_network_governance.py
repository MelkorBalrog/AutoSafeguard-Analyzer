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

from analysis.safety_management import (
    SAFETY_ANALYSIS_WORK_PRODUCTS,
    SafetyManagementToolbox,
    SafetyWorkProduct,
)
from analysis.governance import GovernanceDiagram


def test_causal_bayesian_network_work_product():
    name = "Causal Bayesian Network Analysis"
    assert name in SAFETY_ANALYSIS_WORK_PRODUCTS
    toolbox = SafetyManagementToolbox()
    toolbox.work_products.append(SafetyWorkProduct("Gov", name, ""))
    diagram = GovernanceDiagram.default_from_work_products([name])
    assert diagram.tasks() == [name]
