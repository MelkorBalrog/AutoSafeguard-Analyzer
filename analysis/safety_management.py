"""Safety & Security management data structures.

This module defines simple data classes used by the GUI and other modules to
collect work products, lifecycle information and workflows related to safety
governance."""

"""Helpers for managing safety governance information.

This module originally provided a thin container for safety governance
artifacts.  The user request requires the toolbox to control which work
products are available in the main application.  To support this the
toolbox now tracks which analysis types have been declared in governance
diagrams and how many actual documents of each type exist.  When a work
product type is removed from governance but there are existing documents
of that type, the removal is rejected to prevent orphaned analyses.

The toolbox also notifies listeners (typically the GUI) whenever the set
of enabled work products changes so menu items can be enabled/disabled.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Callable, Optional

from sysml.sysml_repository import SysMLRepository

# Relationships that allow propagation of results between work products. Each
# entry is a directed edge from source to target analysis name.
ALLOWED_PROPAGATIONS: set[tuple[str, str]] = {
    ("HAZOP", "Risk Assessment"),
    ("FI2TC", "Risk Assessment"),
    ("TC2FI", "Risk Assessment"),
    ("Threat Analysis", "Cyber Risk Assessment"),
    ("Cyber Risk Assessment", "Risk Assessment"),
    ("Risk Assessment", "FMEA"),
    ("Risk Assessment", "FMEDA"),
    ("Risk Assessment", "FTA"),
    ("Risk Assessment", "Product Goal Specification"),
    ("FMEA", "FTA"),
    ("FMEDA", "FTA"),
    ("FTA", "Product Goal Specification"),
}

@dataclass
class SafetyWorkProduct:
    """Describe a work product generated from a diagram or analysis."""

    diagram: str
    analysis: str
    rationale: str

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Return a serialisable representation of this work product."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SafetyWorkProduct":
        """Create a work product from *data* mapping."""
        return cls(
            data.get("diagram", ""),
            data.get("analysis", ""),
            data.get("rationale", ""),
        )


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
        """Serialise this module including submodules."""
        return {
            "name": self.name,
            "modules": [m.to_dict() for m in self.modules],
            "diagrams": list(self.diagrams),
        }

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> "GovernanceModule":
        """Recreate a module hierarchy from *data*."""
        mod = cls(data.get("name", ""))
        mod.modules = [cls.from_dict(m) for m in data.get("modules", [])]
        mod.diagrams = list(data.get("diagrams", []))
        return mod


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
    active_module: Optional[str] = None
    # Track how many documents of each analysis type exist.  This allows the
    # toolbox to prevent removal of work product declarations when documents
    # are present.
    work_product_counts: Dict[str, int] = field(default_factory=dict)
    # Map analysis names to document names and their creating module so work
    # products can be filtered by lifecycle phase. Documents without an entry
    # are visible in all phases for backwards compatibility.
    doc_phases: Dict[str, Dict[str, str]] = field(default_factory=dict)
    # Optional callback invoked whenever the enabled work product set changes.
    on_change: Optional[Callable[[], None]] = field(default=None, repr=False)

    # ------------------------------------------------------------------
    def add_work_product(self, diagram: str, analysis: str, rationale: str) -> None:
        """Add a work product linking a diagram to an analysis with rationale."""
        self.work_products.append(SafetyWorkProduct(diagram, analysis, rationale))
        if self.on_change:
            self.on_change()

    # ------------------------------------------------------------------
    def remove_work_product(self, diagram: str, analysis: str) -> bool:
        """Remove a work product declaration if no documents of that type exist.

        Parameters
        ----------
        diagram: str
            Name of the governance diagram containing the declaration.
        analysis: str
            The analysis/work product type to remove.

        Returns
        -------
        bool
            ``True`` when the declaration was removed, ``False`` if it could
            not be removed because there are existing work products of this
            type or the declaration was not found.
        """

        if self.work_product_counts.get(analysis, 0) > 0:
            return False

        for idx, wp in enumerate(list(self.work_products)):
            if wp.diagram == diagram and wp.analysis == analysis:
                del self.work_products[idx]
                if self.on_change:
                    self.on_change()
                return True
        return False

    # ------------------------------------------------------------------
    def register_created_work_product(self, analysis: str, name: str) -> None:
        """Record creation of a work product document of type ``analysis``."""
        self.work_product_counts[analysis] = self.work_product_counts.get(analysis, 0) + 1
        if self.active_module:
            self.doc_phases.setdefault(analysis, {})[name] = self.active_module

    # ------------------------------------------------------------------
    def register_deleted_work_product(self, analysis: str, name: str) -> None:
        """Record deletion of a work product document of type ``analysis``."""
        if self.work_product_counts.get(analysis, 0) > 0:
            self.work_product_counts[analysis] -= 1
        if name:
            self.doc_phases.get(analysis, {}).pop(name, None)

    # ------------------------------------------------------------------
    def rename_document(self, analysis: str, old: str, new: str) -> None:
        """Update phase mapping when a document is renamed."""
        phase = self.doc_phases.get(analysis, {}).pop(old, None)
        if phase:
            self.doc_phases.setdefault(analysis, {})[new] = phase

    # ------------------------------------------------------------------
    def document_visible(self, analysis: str, name: str) -> bool:
        """Return ``True`` if the document should be visible in the active phase."""
        if not self.active_module:
            return True
        phase = self.doc_phases.get(analysis, {}).get(name)
        if phase is None:
            return True
        return phase == self.active_module

    # ------------------------------------------------------------------
    def enabled_products(self) -> set[str]:
        """Return the set of analysis names enabled for the active phase."""
        all_products = {wp.analysis for wp in self.work_products}
        if not self.active_module:
            return all_products
        diagrams = self.diagrams_in_module(self.active_module)
        if not diagrams:
            return all_products
        return {wp.analysis for wp in self.work_products if wp.diagram in diagrams}

    # ------------------------------------------------------------------
    def is_enabled(self, analysis: str) -> bool:
        """Check whether ``analysis`` has been enabled via governance."""
        return analysis in self.enabled_products()

    # ------------------------------------------------------------------
    def set_active_module(self, name: Optional[str]) -> None:
        """Select the active lifecycle phase by module *name*."""
        self.active_module = name
        if self.on_change:
            self.on_change()

    # ------------------------------------------------------------------
    def _find_module(self, name: str, modules: List[GovernanceModule]) -> Optional[GovernanceModule]:
        for mod in modules:
            if mod.name == name:
                return mod
            found = self._find_module(name, mod.modules)
            if found:
                return found
        return None

    # ------------------------------------------------------------------
    def diagrams_in_module(self, name: str) -> set[str]:
        """Return all diagram names contained within module *name*."""
        mod = self._find_module(name, self.modules)
        if not mod:
            return set()

        names: set[str] = set()

        def _collect(m: GovernanceModule) -> None:
            names.update(m.diagrams)
            for sub in m.modules:
                _collect(sub)

        _collect(mod)
        return names

    def list_modules(self) -> List[str]:
        """Return names of all governance modules including submodules."""
        names: List[str] = []

        def _collect(mods: List[GovernanceModule]) -> None:
            for m in mods:
                names.append(m.name)
                _collect(m.modules)

        _collect(self.modules)
        return names

    # ------------------------------------------------------------------
    def rename_module(self, old: str, new: str) -> None:
        """Rename a governance module ensuring uniqueness.

        If ``new`` conflicts with an existing module name the method appends
        a numeric suffix to make it unique. The :attr:`active_module` is updated
        when it references the renamed module.
        """

        if not new or old == new:
            return

        existing = set(self.list_modules())
        existing.discard(old)
        base = new
        suffix = 1
        while new in existing:
            new = f"{base}_{suffix}"
            suffix += 1

        def _rename(mods: List[GovernanceModule]) -> bool:
            for mod in mods:
                if mod.name == old:
                    mod.name = new
                    if self.active_module == old:
                        self.active_module = new
                    return True
                if _rename(mod.modules):
                    return True
            return False

        _rename(self.modules)

    # ------------------------------------------------------------------
    def propagation_type(self, source: str, target: str) -> Optional[str]:
        """Return propagation relationship type from ``source`` to ``target``.

        The method searches all governance diagrams for a connection linking
        the two named work products using one of the propagation relationship
        types. ``None`` is returned when no such link exists."""

        repo = SysMLRepository.get_instance()
        diag_ids = self.diagrams.values()
        if self.active_module:
            names = self.diagrams_in_module(self.active_module)
            diag_ids = [self.diagrams.get(n) for n in names if self.diagrams.get(n)]
        for diag_id in diag_ids:
            diag = repo.diagrams.get(diag_id)
            if not diag:
                continue
            src_id = dst_id = None
            for obj in getattr(diag, "objects", []):
                if obj.get("obj_type") != "Work Product":
                    continue
                name = obj.get("properties", {}).get("name")
                if name == source:
                    src_id = obj.get("obj_id")
                elif name == target:
                    dst_id = obj.get("obj_id")
            if src_id is None or dst_id is None:
                continue
            for c in getattr(diag, "connections", []):
                stereo = (c.get("stereotype") or c.get("conn_type") or "").lower()
                if (
                    c.get("src") == src_id
                    and c.get("dst") == dst_id
                    and stereo
                    in {"propagate", "propagate by review", "propagate by approval"}
                ):
                    mapping = {
                        "propagate": "Propagate",
                        "propagate by review": "Propagate by Review",
                        "propagate by approval": "Propagate by Approval",
                    }
                    return c.get("conn_type") or mapping[stereo]
        return None

    # ------------------------------------------------------------------
    def can_propagate(
        self,
        source: str,
        target: str,
        *,
        reviewed: bool = False,
        joint_review: bool = False,
    ) -> bool:
        """Return ``True`` if results may propagate from ``source`` to ``target``.

        ``Propagate`` links always allow propagation. ``Propagate by Review``
        requires that a peer review has been performed (``reviewed``). ``Propagate
        by Approval`` requires a completed joint review (``joint_review``).
        ``False`` is returned when no propagation relationship exists."""

        rel = self.propagation_type(source, target)
        if rel == "Propagate":
            return True
        if rel == "Propagate by Review":
            return reviewed
        if rel == "Propagate by Approval":
            return joint_review
        return False

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
            "active_module": self.active_module,
            "doc_phases": {k: dict(v) for k, v in self.doc_phases.items()},
        }

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> "SafetyManagementToolbox":
        """Create a toolbox instance from serialized *data*.

        The folder structure is reconstructed using
        :meth:`GovernanceModule.from_dict` ensuring that the Safety & Security Management
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
        toolbox.active_module = data.get("active_module")
        toolbox.doc_phases = {
            k: dict(v) for k, v in data.get("doc_phases", {}).items()
        }
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

