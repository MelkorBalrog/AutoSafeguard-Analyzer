"""Basic data structures for GSN argumentation diagrams."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import uuid


@dataclass
class GSNNode:
    """Represents a node in a GSN argumentation diagram.

    Parameters
    ----------
    user_name:
        Human readable label for the node (name).
    description:
        Optional description shown beneath the name when rendering.
    node_type:
        One of ``Goal``, ``Strategy``, ``Solution``, ``Assumption``,
        ``Justification`` or ``Context``.
    x, y:
        Optional coordinates used when rendering the diagram.
    """

    user_name: str
    node_type: str
    description: str = ""
    x: float = 50
    y: float = 50
    children: List["GSNNode"] = field(default_factory=list)
    parents: List["GSNNode"] = field(default_factory=list)
    is_primary_instance: bool = True
    original: Optional["GSNNode"] = field(default=None, repr=False)
    unique_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    work_product: str = ""
    evidence_link: str = ""

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        # A freshly created node is considered its own original instance.
        if self.original is None:
            self.original = self

    # ------------------------------------------------------------------
    def add_child(self, child: "GSNNode") -> None:
        """Attach *child* to this node, updating parent/child lists."""
        self.children.append(child)
        child.parents.append(self)

    # ------------------------------------------------------------------
    def clone(self, parent: Optional["GSNNode"] = None) -> "GSNNode":
        """Return a copy of this node referencing the same original.

        The clone shares the ``original`` reference with the primary
        instance, enabling multiple diagram occurrences similar to away
        solutions in GSN 2.0.
        """
        clone = GSNNode(
            self.user_name,
            self.node_type,
            description=self.description,
            x=self.x,
            y=self.y,
            is_primary_instance=False,
            original=self.original,
            work_product=self.work_product,
            evidence_link=self.evidence_link,
        )
        if parent is not None:
            parent.add_child(clone)
        return clone

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation of this node."""
        return {
            "unique_id": self.unique_id,
            "user_name": self.user_name,
            "description": self.description,
            "node_type": self.node_type,
            "x": self.x,
            "y": self.y,
            "children": [c.unique_id for c in self.children],
            "is_primary_instance": self.is_primary_instance,
            "original": self.original.unique_id if self.original else None,
            "work_product": self.work_product,
            "evidence_link": self.evidence_link,
        }

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict, nodes: Optional[dict] = None) -> "GSNNode":
        """Reconstruct a :class:`GSNNode` from *data*.

        The *nodes* mapping is used internally to resolve references
        between nodes when loading a full diagram.
        """
        nodes = nodes if nodes is not None else {}
        node = cls(
            data.get("user_name", ""),
            data.get("node_type", "Goal"),
            description=data.get("description", ""),
            x=data.get("x", 50),
            y=data.get("y", 50),
            is_primary_instance=data.get("is_primary_instance", True),
            unique_id=data.get("unique_id", str(uuid.uuid4())),
            work_product=data.get("work_product", ""),
            evidence_link=data.get("evidence_link", ""),
        )
        nodes[node.unique_id] = node
        # Temporarily store child and original references for second pass
        node._tmp_children = list(data.get("children", []))  # type: ignore[attr-defined]
        node._tmp_original = data.get("original")  # type: ignore[attr-defined]
        return node

    # ------------------------------------------------------------------
    @staticmethod
    def resolve_references(nodes: dict) -> None:
        """Resolve child and original references after initial loading."""
        for node in nodes.values():
            children_ids = getattr(node, "_tmp_children", [])
            for cid in children_ids:
                child = nodes.get(cid)
                if child:
                    node.add_child(child)
            orig_id = getattr(node, "_tmp_original", None)
            if orig_id and orig_id in nodes:
                node.original = nodes[orig_id]
            # cleanup temporary attributes
            if hasattr(node, "_tmp_children"):
                delattr(node, "_tmp_children")
            if hasattr(node, "_tmp_original"):
                delattr(node, "_tmp_original")
