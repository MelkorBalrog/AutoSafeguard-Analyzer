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
class GovernanceModule:
    """Container for organising governance diagrams into folders."""

    name: str
    modules: List["GovernanceModule"] = field(default_factory=list)
    diagrams: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation of this module."""
        return {
            "name": self.name,
            "modules": [m.to_dict() for m in self.modules],
            "diagrams": list(self.diagrams),
        }

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> "GovernanceModule":
        """Recreate a :class:`GovernanceModule` from *data*.

        Nested modules are reconstructed recursively so the folder
        hierarchy can be restored exactly as it was when saved.
        """
        return cls(
            data.get("name", ""),
            [cls.from_dict(m) for m in data.get("modules", [])],
            list(data.get("diagrams", [])),
        )


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
    modules: List[GovernanceModule] = field(default_factory=list)

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
    # Persistence helpers
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Return a JSON serialisable representation of the toolbox.

        All dataclass members, including the folder hierarchy stored in
        :attr:`modules`, are converted into primitive Python types so they can
        be saved using :mod:`json` or similar libraries.
        """
        return {
            "work_products": [wp.__dict__ for wp in self.work_products],
            "lifecycle": list(self.lifecycle),
            "workflows": {k: list(v) for k, v in self.workflows.items()},
            "diagrams": dict(self.diagrams),
            "modules": [m.to_dict() for m in self.modules],
        }

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> "SafetyManagementToolbox":
        """Create a toolbox instance from serialized *data*.

        The folder structure is reconstructed using
        :meth:`GovernanceModule.from_dict` ensuring that the Safety Management
        Explorer reflects the saved hierarchy on reload.
        """
        toolbox = cls()
        toolbox.work_products = [
            SafetyWorkProduct(**wp) for wp in data.get("work_products", [])
        ]
        toolbox.lifecycle = list(data.get("lifecycle", []))
        toolbox.workflows = {
            k: list(v) for k, v in data.get("workflows", {}).items()
        }
        toolbox.diagrams = dict(data.get("diagrams", {}))
        toolbox.modules = [
            GovernanceModule.from_dict(m) for m in data.get("modules", [])
        ]
        return toolbox

    # ------------------------------------------------------------------
    def diagram_hierarchy(self) -> List[List[str]]:
        """Return governance diagrams arranged into hierarchy levels.

        Diagrams appear in successive levels when a task in one diagram links
        to another diagram. Any diagrams not referenced by others start at the
        top level. Each level lists diagram names sorted alphabetically.
        """
        self._sync_diagrams()
        repo = SysMLRepository.get_instance()

        edges: dict[str, set[str]] = {d: set() for d in self.diagrams.values()}
        reverse: dict[str, set[str]] = {d: set() for d in self.diagrams.values()}

        for diag_id in edges:
            diag = repo.diagrams.get(diag_id)
            if not diag:
                continue
            for obj in getattr(diag, "objects", []):
                # ``objects`` may contain plain dictionaries from the repository
                # or ``SysMLObject`` instances used by the GUI.  Support both.
                elem_id = (
                    obj.get("element_id") if isinstance(obj, dict) else getattr(obj, "element_id", None)
                )
                if not elem_id:
                    continue

                target = repo.get_linked_diagram(elem_id)

                if not target:
                    # Some diagrams reference others through object properties
                    # rather than explicit repository links. These appear as
                    # ``view`` or ``diagram`` identifiers within the object's
                    # property mapping. Support both dictionary and dataclass
                    # representations.
                    props = (
                        obj.get("properties", {})
                        if isinstance(obj, dict)
                        else getattr(obj, "properties", {})
                    )
                    target = props.get("view") or props.get("diagram")

                if target in edges:
                    edges[diag_id].add(target)
                    reverse[target].add(diag_id)

        roots = sorted(
            (d for d in edges if not reverse[d]),
            key=lambda d: repo.diagrams[d].name,
        )
        levels: List[List[str]] = []
        visited: set[str] = set()
        current = roots
        while current:
            levels.append(sorted(repo.diagrams[d].name for d in current))
            visited.update(current)
            next_level: set[str] = set()
            for d in current:
                next_level.update(child for child in edges[d] if child not in visited)
            current = sorted(next_level, key=lambda d: repo.diagrams[d].name)

        remaining = sorted(
            [d for d in edges if d not in visited],
            key=lambda d: repo.diagrams[d].name,
        )
        for d in remaining:
            levels.append([repo.diagrams[d].name])

        return levels

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

