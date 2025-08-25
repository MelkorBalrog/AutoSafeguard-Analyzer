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
from types import SimpleNamespace

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mainappsrc.models.gsn import GSNNode, GSNDiagram
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from gui.name_utils import (
    collect_work_product_names,
    unique_name_v1,
    unique_name_v2,
    unique_name_v3,
    unique_name_v4,
)


def test_unique_name_variants() -> None:
    existing = {"A", "A_1", "A-1", "A 1", "A (1)"}
    assert unique_name_v1("A", existing) not in existing
    assert unique_name_v2("A", existing) not in existing
    assert unique_name_v3("A", existing) not in existing
    assert unique_name_v4("A", existing) not in existing


def test_same_name_allowed_across_types() -> None:
    root = GSNNode("Shared", "Goal")
    gsn_diag = GSNDiagram(root)
    app = SimpleNamespace(gsn_diagrams=[gsn_diag], gsn_modules=[], cbn_docs=[])

    names_cbn = collect_work_product_names(app, diagram_type="cbn")
    assert unique_name_v4("Shared", names_cbn) == "Shared"
    cbn_doc = CausalBayesianNetworkDoc("Shared")
    app.cbn_docs.append(cbn_doc)

    names_gsn = collect_work_product_names(app, ignore=gsn_diag, diagram_type="gsn")
    assert unique_name_v4("Shared", names_gsn) == "Shared"

    names_cbn = collect_work_product_names(app, diagram_type="cbn")
    assert unique_name_v4("Shared", names_cbn) != "Shared"
