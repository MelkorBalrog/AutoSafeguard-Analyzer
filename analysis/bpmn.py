"""Basic BPMN diagram support for safety governance workflows."""

from dataclasses import dataclass, field
from typing import List, Tuple

import networkx as nx


@dataclass
class BPMNDiagram:
    """A very small BPMN-like diagram using a directed graph.

    Nodes in the graph represent tasks and edges represent sequence flows.
    The diagram is intentionally lightweight but can be tailored and extended
    by users to model project-specific safety governance workflows.
    """

    graph: nx.DiGraph = field(default_factory=nx.DiGraph)

    def add_task(self, name: str) -> None:
        """Add a task node to the diagram."""
        self.graph.add_node(name)

    def add_flow(self, src: str, dst: str) -> None:
        """Add a directed flow between two existing tasks."""
        if not self.graph.has_node(src) or not self.graph.has_node(dst):
            raise ValueError("Both tasks must exist before creating a flow")
        self.graph.add_edge(src, dst)

    def tasks(self) -> List[str]:
        """Return all task node names in the diagram."""
        return list(self.graph.nodes())

    def flows(self) -> List[Tuple[str, str]]:
        """Return all directed flows (edges) in the diagram."""
        return list(self.graph.edges())

    @classmethod
    def default_from_work_products(cls, names: List[str]) -> "BPMNDiagram":
        """Create a default sequential diagram from the given work products."""
        diagram = cls()
        for name in names:
            diagram.add_task(name)
        tasks = diagram.tasks()
        for src, dst in zip(tasks, tasks[1:]):
            diagram.add_flow(src, dst)
        return diagram
