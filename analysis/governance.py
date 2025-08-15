"""Basic governance diagram support for safety workflows."""

from dataclasses import dataclass, field
from typing import Any, Iterator, List, Tuple

from pathlib import Path
from config import load_json_with_comments

import networkx as nx

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config/diagram_rules.json"
_CONFIG = load_json_with_comments(_CONFIG_PATH)

# Element and relationship types associated with AI & safety lifecycle nodes.
_AI_NODES = set(_CONFIG.get("ai_nodes", []))
_AI_RELATIONS = set(_CONFIG.get("ai_relations", []))

# Map relationship labels or connection types to requirement actions.  Each
# entry defines the verb to use, whether the destination element acts as a
# constraint instead of an object, and an optional default subject.  The
# resulting requirement follows the ISO/IEC/IEEE 29148 pattern
# ``[CND] <SUB> shall <ACT> [OBJ] [CON].``
_RELATIONSHIP_RULES: dict[str, dict[str, str | bool]] = _CONFIG.get(
    "relationship_rules", {}
)

# Map node types to default requirement roles so that the generator can
# identify the subject, object or constraint directly from the model.
_NODE_ROLES = _CONFIG.get("node_roles", {})


def reload_config() -> None:
    """Reload governance-related configuration."""
    global _CONFIG, _AI_NODES, _AI_RELATIONS, _RELATIONSHIP_RULES, _NODE_ROLES
    _CONFIG = load_json_with_comments(_CONFIG_PATH)
    _AI_NODES = set(_CONFIG.get("ai_nodes", []))
    _AI_RELATIONS = set(_CONFIG.get("ai_relations", []))
    _RELATIONSHIP_RULES = _CONFIG.get("relationship_rules", {})
    _NODE_ROLES = _CONFIG.get("node_roles", {})


@dataclass
class GeneratedRequirement:
    """Structured requirement composed from diagram elements.

    The dataclass exposes the individual requirement components (condition,
    subject, action, object and constraint) alongside the requirement
    category.  Each field except ``action`` is optional and therefore given a
    default value.  This ordering avoids the ``TypeError`` raised when optional
    fields precede required ones in a :func:`dataclass` definition and mirrors
    how requirements are instantiated in the generator.
    """

    action: str
    condition: str | None = None
    subject: str | None = None
    obj: str | None = None
    constraint: str | None = None
    origin: str | None = None
    req_type: str = "organizational"

    @property
    def text(self) -> str:
        parts: List[str] = []
        if self.condition:
            parts.append(f"If {self.condition},")
        if self.origin:
            parts.append(f"after '{self.origin}',")
        subject = self.subject or "Task"
        main = f"{subject} shall {self.action}"
        if self.obj:
            main += f" '{self.obj}'"
        if self.constraint:
            main += f" '{self.constraint}'"
        main += "."
        parts.append(main)
        return " ".join(parts)

    def __iter__(self) -> Iterator[str]:
        yield self.text
        yield self.req_type

    def __getitem__(self, idx: int) -> str:
        return (self.text, self.req_type)[idx]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.text

    def __contains__(self, item: str) -> bool:  # pragma: no cover - trivial
        return item in self.text or item in self.req_type


@dataclass
class GovernanceDiagram:
    """A very small governance diagram using a directed graph.

    Nodes in the graph represent tasks and edges represent sequence flows.
    The diagram is intentionally lightweight but can be tailored and extended
    by users to model project-specific safety governance workflows.
    """

    graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    # Explicit mapping of edges to their metadata so the diagram works even
    # when :mod:`networkx` is not fully featured.
    edge_data: dict[tuple[str, str], dict[str, str | None]] = field(
        default_factory=dict
    )
    # Track the original diagram object type for each task so requirements can
    # be categorised.  Tasks originating from AI & safety nodes produce AI
    # safety requirements.
    node_types: dict[str, str] = field(default_factory=dict)

    def _role_for(self, name: str) -> str:
        """Return the requirement role for a node name."""
        ntype = self.node_types.get(name, "")
        return _NODE_ROLES.get(ntype, "object")

    def add_task(self, name: str, node_type: str = "Action") -> None:
        """Add a task node to the diagram."""
        self.graph.add_node(name)
        self.node_types[name] = node_type

    def add_flow(
        self,
        src: str,
        dst: str,
        condition: str | None = None,
        conn_type: str = "Flow",
    ) -> None:
        """Add a directed flow between two existing tasks.

        Parameters
        ----------
        src, dst:
            Names of the existing source and destination tasks.
        condition:
            Optional textual condition that must hold for the flow to occur.
        conn_type:
            Connection type from the original diagram; defaults to ``"Flow"``.
        """

        if not self.graph.has_node(src) or not self.graph.has_node(dst):
            raise ValueError("Both tasks must exist before creating a flow")
        self.graph.add_edge(src, dst)
        self.edge_data[(src, dst)] = {
            "kind": "flow",
            "condition": condition,
            "label": None,
            "conn_type": conn_type,
        }

    def add_relationship(
        self,
        src: str,
        dst: str,
        condition: str | None = None,
        label: str | None = None,
        conn_type: str | None = None,
    ) -> None:
        """Add a non-flow relationship between two existing tasks.

        Parameters
        ----------
        src, dst:
            Names of the existing source and destination tasks.
        condition:
            Optional textual condition that must hold for the relationship.
        label:
            Optional label describing the relationship between the tasks.
        conn_type:
            Connection type from the original diagram, used to determine the
            requirement category.
        """

        if not self.graph.has_node(src) or not self.graph.has_node(dst):
            raise ValueError("Both tasks must exist before creating a relationship")
        self.graph.add_edge(src, dst)
        self.edge_data[(src, dst)] = {
            "kind": "relationship",
            "condition": condition,
            "label": label,
            "conn_type": conn_type,
        }

    def tasks(self) -> List[str]:
        """Return all task node names in the diagram."""
        return list(self.graph.nodes())

    def flows(self) -> List[Tuple[str, str]]:
        """Return all directed flow edges in the diagram."""
        edges: List[Tuple[str, str]] = []
        for u, v in self.graph.edges():
            data = self.edge_data.get((u, v))
            if data is None or data.get("kind") == "flow":
                edges.append((u, v))
        return edges

    def relationships(self) -> List[Tuple[str, str]]:
        """Return all non-flow relationships in the diagram."""
        return [
            (u, v)
            for (u, v), data in self.edge_data.items()
            if data.get("kind") == "relationship"
        ]

    def generate_requirements(self) -> List[GeneratedRequirement | tuple[str, str]]:
        """Generate structured requirements from the diagram."""

        requirements: List[GeneratedRequirement | tuple[str, str]] = []

        decision_sources: dict[str, str] = {}
        for src, dst in self.graph.edges():
            if self.node_types.get(dst) == "Decision":
                decision_sources[dst] = src

        for src, dst in self.graph.edges():
            if self.node_types.get(dst) == "Decision":
                continue

            data = self.edge_data.get(
                (src, dst), {"kind": "flow", "condition": None, "label": None}
            )
            cond = data.get("condition")
            kind = data.get("kind")
            label = data.get("label")
            conn_type = data.get("conn_type")

            # Skip standalone reuse links between lifecycle phases. The
            # corresponding transition requirement will incorporate reuse
            # information so an additional requirement would be redundant.
            if (
                conn_type == "Re-use"
                and self.node_types.get(src) == "Lifecycle Phase"
                and self.node_types.get(dst) == "Lifecycle Phase"
            ):
                continue

            req_type = "organizational"
            if (
                conn_type in _AI_RELATIONS
                or self.node_types.get(src) in _AI_NODES
                or self.node_types.get(dst) in _AI_NODES
            ):
                req_type = "AI safety"

            # Express lifecycle phase transitions explicitly.
            if (
                kind == "flow"
                and self.node_types.get(src) == "Lifecycle Phase"
                and self.node_types.get(dst) == "Lifecycle Phase"
            ):
                reuse_edge = self.edge_data.get((dst, src), {})
                has_reuse = reuse_edge.get("conn_type") == "Re-use"
                text = f"{src} shall transition to '{dst}'"
                if has_reuse:
                    text += f" reusing outputs from '{src}'"
                if cond:
                    text += f" only after {cond}"
                text += "."
                requirements.append((text, req_type))
                continue

            origin = None
            subject = src
            obj: str | None = dst
            constraint: str | None = None
            action: str
            explicit_subject = None

            if self.node_types.get(src) == "Decision":
                origin = decision_sources.get(src)
                if origin and kind == "flow":
                    subject = origin
            if kind == "flow":
                action = "precede"
            else:
                key = (label or conn_type or "").lower()
                rule = _RELATIONSHIP_RULES.get(key, {})
                action = str(rule.get("action", label or "relate to"))
                explicit_subject = rule.get("subject")
                if explicit_subject:
                    subject = str(explicit_subject)
                if rule.get("constraint"):
                    constraint = dst
                    obj = None
                elif not label and not rule:
                    action = "be related to"

            if obj is not None:
                s_role = self._role_for(subject)
                d_role = self._role_for(obj)
                if s_role != "subject" and d_role == "subject":
                    subject, obj = obj, subject

            requirements.append(
                GeneratedRequirement(
                    action=action,
                    condition=cond,
                    subject=subject,
                    obj=obj,
                    constraint=constraint,
                    origin=origin if (origin and kind != "flow") else None,
                    req_type=req_type,
                )
            )

        return requirements

    @classmethod
    def default_from_work_products(cls, names: List[str]) -> "GovernanceDiagram":
        """Create a default sequential diagram from the given work products."""
        diagram = cls()
        for name in names:
            diagram.add_task(name)
        tasks = diagram.tasks()
        for src, dst in zip(tasks, tasks[1:]):
            diagram.add_flow(src, dst)
        return diagram

    @classmethod
    def from_repository(cls, repo: Any, diag_id: str) -> "GovernanceDiagram":
        """Build a :class:`GovernanceDiagram` from a repository diagram.

        Parameters
        ----------
        repo:
            Repository instance providing ``diagrams`` and ``elements`` maps.
        diag_id:
            Identifier of the governance diagram to convert.
        """

        diagram = cls()
        src_diagram = repo.diagrams.get(diag_id)
        if not src_diagram:
            return diagram

        id_to_name: dict[int, str] = {}
        decision_sources: dict[int, str] = {}
        for obj in getattr(src_diagram, "objects", []):
            odict = obj if isinstance(obj, dict) else obj.__dict__
            obj_type = odict.get("obj_type")
            obj_id = odict.get("obj_id")
            if obj_type == "Decision":
                decision_sources[obj_id] = ""
            elem_id = odict.get("element_id")
            name = ""
            if elem_id and elem_id in repo.elements:
                name = repo.elements[elem_id].name
            if not name:
                name = odict.get("properties", {}).get("name", "")
            if name:
                diagram.add_task(name, node_type=obj_type or "Action")
                id_to_name[obj_id] = name

        # Map decision nodes to their predecessor action
        for conn in getattr(src_diagram, "connections", []):
            cdict = conn if isinstance(conn, dict) else conn.__dict__
            if cdict.get("conn_type") != "Flow":
                continue
            src_name = id_to_name.get(cdict.get("src"))
            dst_id = cdict.get("dst")
            if src_name and dst_id in decision_sources:
                decision_sources[dst_id] = src_name

        # Map decision nodes to their predecessor action
        for conn in getattr(src_diagram, "connections", []):
            cdict = conn if isinstance(conn, dict) else conn.__dict__
            src_id = cdict.get("src")
            dst_id = cdict.get("dst")
            name = cdict.get("name")
            props = cdict.get("properties", {})
            cond = props.get("condition")
            if not cond:
                guard = cdict.get("guard")
                if guard:
                    ops = cdict.get("guard_ops") or []
                    sep = f" {ops[0]} " if ops else " AND "
                    cond = sep.join(guard)
                elif name and cdict.get("conn_type") == "Flow":
                    cond = name
            conn_type = cdict.get("conn_type")
            cond_prop = cdict.get("properties", {}).get("condition")
            guards = cdict.get("guard") or []
            guard_ops = cdict.get("guard_ops") or []
            if isinstance(guards, str):
                guards = [guards]
            if isinstance(guard_ops, str):
                guard_ops = [guard_ops]
            guard_text: str | None = None
            if guards:
                parts: list[str] = []
                for i, g in enumerate(guards):
                    if i == 0:
                        parts.append(g)
                    else:
                        op = guard_ops[i - 1] if i - 1 < len(guard_ops) else "AND"
                        parts.append(f"{op} {g}")
                guard_text = " ".join(parts)
            if cdict.get("conn_type") == "Flow":
                cond = cond_prop or guard_text or name
                src = id_to_name.get(src_id)
                dst = id_to_name.get(dst_id)
                if src and dst:
                    diagram.add_flow(src, dst, cond)
                elif src_id in decision_sources and dst:
                    prev = decision_sources.get(src_id)
                    if prev:
                        diagram.add_flow(prev, dst, cond)
            else:
                src = id_to_name.get(src_id) or decision_sources.get(src_id)
                dst = id_to_name.get(dst_id)
                if not src or not dst:
                    continue
                cond = cond_prop or guard_text
                if cond is None and name is not None:
                    diagram.add_relationship(src, dst, condition=name, conn_type=conn_type)
                else:
                    diagram.add_relationship(
                        src, dst, condition=cond, label=name, conn_type=conn_type
                    )

        return diagram

if __name__ == "__main__":  # pragma: no cover - example usage for docs
    demo = GovernanceDiagram()
    demo.add_task("Draft Plan")
    demo.add_task("Review Plan")
    demo.add_flow("Draft Plan", "Review Plan")
    demo.add_relationship(
        "Review Plan", "Draft Plan", condition="changes requested", label="rework"
    )
    for requirement in demo.generate_requirements():
        print(requirement)
