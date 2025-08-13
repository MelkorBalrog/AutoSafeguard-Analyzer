"""Safety management data structures.

This module defines simple data classes used by the GUI and other modules to
collect work products, lifecycle information and workflows related to safety
governance."""

from dataclasses import dataclass, field
from typing import Dict, List

from sysml.sysml_repository import SysMLRepository

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
    diagrams: Dict[str, str] = field(default_factory=dict)

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

    # ------------------------------------------------------------------
    # Diagram management helpers
    # ------------------------------------------------------------------
    def create_diagram(self, name: str) -> str:
        """Create a new BPMN Diagram tracked by this toolbox.

        Parameters
        ----------
        name: str
            Human readable name of the diagram.

        Returns
        -------
        str
            The repository identifier of the created diagram.
        """
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("BPMN Diagram", name=name)
        diag.tags.append("safety-management")
        self.diagrams[name] = diag.diag_id
        return diag.diag_id

    def delete_diagram(self, name: str) -> None:
        """Remove a diagram from the toolbox and repository."""
        diag_id = self.diagrams.pop(name, None)
        if not diag_id:
            return
        repo = SysMLRepository.get_instance()
        repo.delete_diagram(diag_id)

    def rename_diagram(self, old: str, new: str) -> None:
        """Rename a managed diagram ensuring the name remains unique.

        Parameters
        ----------
        old: str
            Current diagram name.
        new: str
            Desired new name for the diagram.
        """
        diag_id = self.diagrams.get(old)
        if not diag_id or not new:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.diagrams.get(diag_id)
        if not diag:
            return

        # Ensure the new name is unique across all diagrams
        existing = {d.name for d in repo.diagrams.values() if d.diag_id != diag_id}
        base = new
        suffix = 1
        while new in existing:
            new = f"{base}_{suffix}"
            suffix += 1

        diag.name = new
        repo.touch_diagram(diag_id)
        del self.diagrams[old]
        self.diagrams[new] = diag_id

    def list_diagrams(self) -> List[str]:
        """Return the names of all managed diagrams.

        Any BPMN Diagram in the repository tagged with
        ``"safety-management"`` should appear in the toolbox even if it
        was created outside of :meth:`create_diagram`. To ensure the list is
        complete we rescan the repository on each call and synchronize the
        internal ``diagrams`` mapping.
        """
        self._sync_diagrams()
        return list(self.diagrams.keys())

    # ------------------------------------------------------------------
    def _sync_diagrams(self) -> None:
        """Synchronize ``self.diagrams`` with repository contents.

        Any diagram tagged ``"safety-management"`` is added to the mapping
        and entries for diagrams that no longer exist are dropped.
        """
        repo = SysMLRepository.get_instance()
        current = {
            d.name: d.diag_id
            for d in repo.diagrams.values()
            if "safety-management" in getattr(d, "tags", [])
        }
        self.diagrams.clear()
        self.diagrams.update(current)

