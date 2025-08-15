"""Basic governance diagram support for safety workflows."""

from dataclasses import dataclass, field
from typing import Any, Iterator, List, Tuple

import networkx as nx

# Element and relationship types associated with AI & safety lifecycle nodes.
_AI_NODES = {"Database", "ANN", "Data acquisition"}
_AI_RELATIONS = {
    "Annotation",
    "Synthesis",
    "Augmentation",
    "Acquisition",
    "Labeling",
    "Field risk evaluation",
    "Field data collection",
    "AI training",
    "AI re-training",
    "Curation",
    "Ingestion",
    "Model evaluation",
}

# Node type groupings for requirement component extraction.
_SUBJECT_NODE_TYPES = {"Role", "Actor", "Stakeholder", "Organization", "Business Unit"}
_ACTION_NODE_TYPES = {
    "Process",
    "Procedure",
    "Activity",
    "Task",
    "Action",
    "Control",
    "Mechanism",
}
_OBJECT_NODE_TYPES = {"Document", "Artifact", "Data", "Record", "Resource"}
_CONSTRAINT_NODE_TYPES = {
    "Policy",
    "Principle",
    "Standard",
    "Guideline",
    "Metric",
    "KPI",
}


@dataclass
class GeneratedRequirement:
    """Container for a generated requirement.

    ``GeneratedRequirement`` stores the individual requirement components so
    governance diagrams can be translated into structured statements following
    ISO/IEC/IEEE 29148.  The object still behaves like both a tuple
    ``(text, type)`` and a string so existing code and tests that expect either
    representation continue to work.
    """

    text: str
    req_type: str
    cnd: str | None = None  # Condition
    sub: str | None = None  # Subject
    act: str | None = None  # Action
    obj: str | None = None  # Object
    con: str | None = None  # Constraint

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

    def generate_requirements(self) -> List[GeneratedRequirement]:
        """Generate structured requirements from the diagram.

        Diagram elements are mapped onto requirement components following the
        ``[CND] SUB shall ACT [OBJ] [CON]`` pattern.  The resulting
        :class:`GeneratedRequirement` objects preserve these components to aid
        downstream tooling.
        """

        requirements: List[GeneratedRequirement] = []

        def compose(cnd: str | None, sub: str, act: str, obj: str | None = None, con: str | None = None) -> str:
            parts: list[str] = []
            if cnd:
                parts.append(f"If {cnd}, ")
            parts.append(f"{sub} shall {act}")
            if obj:
                parts.append(f" {obj}")
            if con:
                parts.append(f" {con}")
            return "".join(parts) + "."

        def req_type_for(conn_type: str | None, src: str, dst: str) -> str:
            if (
                conn_type in _AI_RELATIONS
                or self.node_types.get(src) in _AI_NODES
                or self.node_types.get(dst) in _AI_NODES
            ):
                return "AI safety"
            return "organizational"

        for task in self.tasks():
            ntype = self.node_types.get(task)
            if ntype not in _ACTION_NODE_TYPES:
                continue
            req_type = "AI safety" if ntype in _AI_NODES else "organizational"
            sub = "The system"
            act = f"perform {task}"
            text = compose(None, sub, act)
            requirements.append(
                GeneratedRequirement(text, req_type, sub=sub, act=act)
            )

        for src, dst in self.graph.edges():
            data = self.edge_data.get(
                (src, dst), {"kind": "flow", "condition": None, "label": None}
            )
            cond = data.get("condition")
            kind = data.get("kind")
            label = data.get("label")
            conn_type = data.get("conn_type")
            dst_type = self.node_types.get(dst)
            sub = f"Task '{src}'"

            if kind == "flow":
                act = "precede"
                obj = f"task '{dst}'"
                text = compose(cond, sub, act, obj=obj)
                requirements.append(
                    GeneratedRequirement(
                        text,
                        req_type_for(conn_type, src, dst),
                        cnd=cond,
                        sub=sub,
                        act=act,
                        obj=obj,
                    )
                )
                continue

            # relationship
            if dst_type in _CONSTRAINT_NODE_TYPES or (
                label and label.lower() in {"governed by", "constrained by"}
            ):
                if label:
                    lower = label.lower()
                    act = f"be {lower}" if lower in {"governed by", "constrained by"} else label
                else:
                    act = "comply with"
                con = dst
                text = compose(cond, sub, act, con=con)
                requirements.append(
                    GeneratedRequirement(
                        text,
                        req_type_for(conn_type, src, dst),
                        cnd=cond,
                        sub=sub,
                        act=act,
                        con=con,
                    )
                )
            else:
                act = label if label else "relate to"
                obj = (
                    f"task '{dst}'" if dst_type in _ACTION_NODE_TYPES else dst
                )
                text = compose(cond, sub, act, obj=obj)
                requirements.append(
                    GeneratedRequirement(
                        text,
                        req_type_for(conn_type, src, dst),
                        cnd=cond,
                        sub=sub,
                        act=act,
                        obj=obj,
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
                continue
            elem_id = odict.get("element_id")
            name = ""
            if elem_id and elem_id in repo.elements:
                name = repo.elements[elem_id].name
            if not name:
                name = odict.get("properties", {}).get("name", "")
            if not name:
                continue
            diagram.add_task(name)
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
                src = id_to_name.get(src_id)
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
