"""Safety management data structures.

This module defines simple data classes used by the GUI and other modules to
collect work products, lifecycle information and workflows related to safety
governance.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from .bpmn import BPMNDiagram

@dataclass
class SafetyWorkProduct:
    """Describe a work product generated from a diagram or analysis."""

    diagram: str
    analysis: str
    rationale: str


@dataclass
class LifecycleStage:
    """Represent a single stage in a safety lifecycle."""

    name: str


@dataclass
class Workflow:
    """Ordered list of steps for a named workflow."""

    name: str
    steps: List[str]


@dataclass
class SafetyManagementToolbox:
    """Collect work products and governance artifacts for safety management.

    The toolbox lets users register work products from various diagrams and
    analyses with an associated rationale. It also stores lifecycle stages and
    named workflows so projects can describe their safety governance.
    """

    work_products: List[SafetyWorkProduct] = field(default_factory=list)
    lifecycle: List[str] = field(default_factory=list)
    workflows: Dict[str, List[str]] = field(default_factory=dict)
    business_diagram: BPMNDiagram = field(default_factory=BPMNDiagram)

    def add_work_product(self, diagram: str, analysis: str, rationale: str) -> None:
        """Add a work product linking a diagram to an analysis with rationale."""
        self.work_products.append(SafetyWorkProduct(diagram, analysis, rationale))

    def build_lifecycle(self, stages: List[str]) -> None:
        """Define the project lifecycle stages."""
        self.lifecycle = stages

    def define_workflow(self, name: str, steps: List[str]) -> None:
        """Record an ordered list of steps for a workflow."""
        self.workflows[name] = steps

    def get_work_products(self) -> List[SafetyWorkProduct]:
        """Return all registered work products."""
        return list(self.work_products)

    def get_workflow(self, name: str) -> List[str]:
        """Return the steps for the requested workflow."""
        return self.workflows.get(name, [])

    # Business diagram helpers -------------------------------------------------

    def build_default_diagram(self) -> None:
        """Construct a sequential BPMN diagram from current work products."""
        names = [wp.diagram for wp in self.work_products]
        self.business_diagram = BPMNDiagram.default_from_work_products(names)

    def add_business_task(self, name: str) -> None:
        """Add an arbitrary task to the business diagram."""
        self.business_diagram.add_task(name)

    def add_business_flow(self, src: str, dst: str) -> None:
        """Connect two tasks in the business diagram."""
        self.business_diagram.add_flow(src, dst)