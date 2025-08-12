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
        )
        if parent is not None:
            parent.add_child(clone)
        return clone
