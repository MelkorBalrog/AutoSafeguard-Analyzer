from __future__ import annotations

"""Data structures for safety & security cases."""

from dataclasses import dataclass, field
from typing import List

from gsn import GSNDiagram, GSNNode


@dataclass
class SafetyCase:
    """Representation of a safety & security case derived from a GSN diagram."""

    name: str
    diagram: GSNDiagram
    solutions: List[GSNNode] = field(default_factory=list)

    def collect_solutions(self) -> None:
        """Populate :attr:`solutions` with all solution nodes from ``diagram``."""
        self.solutions = [n for n in self.diagram.nodes if n.node_type == "Solution"]


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
