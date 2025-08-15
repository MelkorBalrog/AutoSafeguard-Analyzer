"""Basic governance diagram support for safety workflows."""

from dataclasses import dataclass, field
from typing import Any, List, Tuple

import networkx as nx


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

    def add_task(self, name: str) -> None:
        """Add a task node to the diagram."""
        self.graph.add_node(name)

    def add_flow(self, src: str, dst: str, condition: str | None = None) -> None:
        """Add a directed flow between two existing tasks.

        Parameters
        ----------
        src, dst:
            Names of the existing source and destination tasks.
        condition:
            Optional textual condition that must hold for the flow to occur.
        """

        if not self.graph.has_node(src) or not self.graph.has_node(dst):
            raise ValueError("Both tasks must exist before creating a flow")
        self.graph.add_edge(src, dst)
        self.edge_data[(src, dst)] = {"kind": "flow", "condition": condition}

    def add_relationship(
        self,
        src: str,
        dst: str,
        condition: str | None = None,
        label: str | None = None,
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
        """

        if not self.graph.has_node(src) or not self.graph.has_node(dst):
            raise ValueError("Both tasks must exist before creating a relationship")
        self.graph.add_edge(src, dst)
        self.edge_data[(src, dst)] = {
            "kind": "relationship",
            "condition": condition,
            "label": label,
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

    def generate_requirements(self) -> List[str]:
        """Generate textual requirements from the diagram.

        Tasks, flows, relationships and any optional conditions or labels are
        converted into simple natural language statements for downstream
        processing or documentation.
        """

        requirements: List[str] = []

        for task in self.tasks():
            requirements.append(f"The system shall perform task '{task}'.")

        for src, dst in self.graph.edges():
            data = self.edge_data.get(
                (src, dst), {"kind": "flow", "condition": None, "label": None}
            )
            cond = data.get("condition")
            kind = data.get("kind")
            label = data.get("label")
            if kind == "flow":
                if cond:
                    req = f"When {cond}, task '{src}' shall precede task '{dst}'."
                else:
                    req = f"Task '{src}' shall precede task '{dst}'."
            else:  # relationship
                if label:
                    if cond:
                        req = (
                            f"Task '{src}' shall {label} task '{dst}' when {cond}."
                        )
                    else:
                        req = f"Task '{src}' shall {label} task '{dst}'."
                else:
                    if cond:
                        req = (
                            f"Task '{src}' shall be related to task '{dst}' when {cond}."
                        )
                    else:
                        req = f"Task '{src}' shall be related to task '{dst}'."
            requirements.append(req)

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
            otype = odict.get("obj_type")
            if otype == "Action":
                elem_id = odict.get("element_id")
                name = ""
                if elem_id and elem_id in repo.elements:
                    name = repo.elements[elem_id].name
                if not name:
                    name = odict.get("properties", {}).get("name", "")
                if not name:
                    continue
                diagram.add_task(name)
                id_to_name[odict.get("obj_id")] = name
            elif otype == "Decision":
                decision_sources[odict.get("obj_id")] = ""

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
                    # Backwards compatibility: older diagrams used the name as the condition
                    diagram.add_relationship(src, dst, condition=name)
                else:
                    diagram.add_relationship(src, dst, condition=cond, label=name)

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
