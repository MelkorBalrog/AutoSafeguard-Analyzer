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

from __future__ import annotations

"""Data structures for safety & security reports."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from mainappsrc.models.gsn import GSNDiagram, GSNNode
from config import load_report_template


@dataclass
class SafetyCase:
    """Representation of a safety & security report derived from a GSN diagram."""

    name: str
    diagram: GSNDiagram
    solutions: List[GSNNode] = field(default_factory=list)

    def collect_solutions(self) -> None:
        """Populate :attr:`solutions` with all solution nodes from ``diagram``."""
        self.solutions = [n for n in self.diagram.nodes if n.node_type == "Solution"]

    def build_report_template(self) -> dict:
        """Return safety & security report template filtered by referenced work products."""

        base = load_report_template(
            Path(__file__).resolve().parents[1]
            / "config"
            / "templates"
            / "safety_security_report_template.json"
        )

        # map lower-case keywords to (element placeholder, section title)
        mapping = {
            "fta": ("fta_diagrams", "Fault Tree Analyses (FTA)"),
            "hazard": ("hazard_analysis_diagrams", "Hazard Analyses"),
            "fmea": ("fmea_diagrams", "FMEA Analyses"),
            "fmeda": ("fmeda_diagrams", "FMEDA Analyses"),
            "reliability": ("reliability_analysis", "Reliability Analysis"),
        }

        referenced = {
            getattr(sol, "work_product", "").lower()
            for sol in self.solutions
            if getattr(sol, "work_product", "")
        }

        sections = base.get("sections", [])
        insert_at = len(sections)
        for idx, sec in enumerate(sections):
            if sec.get("title") == "Work Products and Evidence":
                insert_at = idx
                break

        dynamic = []
        for key, (element, title) in mapping.items():
            if any(key in wp for wp in referenced):
                dynamic.append({"title": title, "content": f"<{element}>"})

        base["sections"] = sections[:insert_at] + dynamic + sections[insert_at:]
        return base


@dataclass
class SafetyCaseLibrary:
    """Container managing multiple :class:`SafetyCase` instances."""

    cases: List[SafetyCase] = field(default_factory=list)

    def create_case(self, name: str, diagram: GSNDiagram) -> SafetyCase:
        case = SafetyCase(name, diagram)
        case.collect_solutions()
        self.cases.append(case)
        return case

    def delete_case(self, case: SafetyCase) -> None:
        if case in self.cases:
            self.cases.remove(case)

    def rename_case(self, case: SafetyCase, new_name: str) -> None:
        case.name = new_name

    def list_cases(self) -> List[SafetyCase]:
        return list(self.cases)
