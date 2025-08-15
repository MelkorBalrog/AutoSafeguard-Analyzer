"""Basic governance diagram support for safety workflows."""

from dataclasses import dataclass, field
from typing import List, Tuple

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
        self, src: str, dst: str, condition: str | None = None
    ) -> None:
        """Add a non-flow relationship between two existing tasks."""
        if not self.graph.has_node(src) or not self.graph.has_node(dst):
            raise ValueError("Both tasks must exist before creating a relationship")
        self.graph.add_edge(src, dst)
        self.edge_data[(src, dst)] = {
            "kind": "relationship",
            "condition": condition,
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

        Tasks, flows, relationships and any optional conditions are converted
        into simple natural language statements for downstream processing or
        documentation.
        """

        requirements: List[str] = []

        for task in self.tasks():
            requirements.append(f"The system shall perform task '{task}'.")

        for src, dst in self.graph.edges():
            data = self.edge_data.get((src, dst), {"kind": "flow", "condition": None})
            cond = data.get("condition")
            kind = data.get("kind")
            if kind == "flow":
                if cond:
                    req = f"When {cond}, task '{src}' shall precede task '{dst}'."
                else:
                    req = f"Task '{src}' shall precede task '{dst}'."
            else:  # relationship
                if cond:
                    req = f"Task '{src}' shall be related to task '{dst}' when {cond}."
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


if __name__ == "__main__":  # pragma: no cover - example usage for docs
    demo = GovernanceDiagram()
    demo.add_task("Draft Plan")
    demo.add_task("Review Plan")
    demo.add_flow("Draft Plan", "Review Plan")
    demo.add_relationship("Review Plan", "Draft Plan", "changes requested")
    for requirement in demo.generate_requirements():
        print(requirement)
