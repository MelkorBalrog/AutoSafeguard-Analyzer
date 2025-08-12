"""Data structures for safety governance artifacts."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SafetyWorkProduct:
    """Describe a work product generated from a diagram or analysis."""

    diagram: str
    analysis: str
    rationale: str


@dataclass
class LifecycleStage:
    """Represent a single stage in the project lifecycle."""

    name: str


@dataclass
class SafetyWorkflow:
    """A named workflow with its ordered list of steps."""

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
    lifecycle: List[LifecycleStage] = field(default_factory=list)
    workflows: Dict[str, SafetyWorkflow] = field(default_factory=dict)

    def add_work_product(self, diagram: str, analysis: str, rationale: str) -> None:
        """Add a work product linking a diagram to an analysis with rationale."""

        self.work_products.append(SafetyWorkProduct(diagram, analysis, rationale))

    def build_lifecycle(self, stages: List[str]) -> None:
        """Define the project lifecycle stages."""

        self.lifecycle = [LifecycleStage(name) for name in stages]

    def define_workflow(self, name: str, steps: List[str]) -> None:
        """Record an ordered list of steps for a workflow."""

        self.workflows[name] = SafetyWorkflow(name, steps)

    def get_work_products(self) -> List[SafetyWorkProduct]:
        """Return all registered work products."""

        return list(self.work_products)

    def get_workflow(self, name: str) -> List[str]:
        """Return the steps for the requested workflow."""

        workflow = self.workflows.get(name)
        return workflow.steps if workflow else []


__all__ = [
    "SafetyWorkProduct",
    "LifecycleStage",
    "SafetyWorkflow",
    "SafetyManagementToolbox",
]

