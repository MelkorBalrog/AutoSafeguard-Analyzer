"""Simple rendering support for GSN diagrams."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List
import uuid

from .nodes import GSNNode
from gui.drawing_helper import GSNDrawingHelper


@dataclass
class GSNDiagram:
    """A very small helper to render a GSN argumentation diagram.

    This class is intentionally lightweight; it mirrors a subset of the
    fault tree diagram functionality so that GSN diagrams can reuse the
    existing drawing infrastructure.
    """

    root: GSNNode
    drawing_helper: GSNDrawingHelper = field(default_factory=GSNDrawingHelper)
    diag_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nodes: List[GSNNode] = field(default_factory=list)

    def __post_init__(self) -> None:  # pragma: no cover - simple bookkeeping
        if self.root not in self.nodes:
            self.nodes.append(self.root)

    # ------------------------------------------------------------------
    def add_node(self, node: GSNNode) -> None:
        """Register *node* with the diagram without connecting it."""
        if node not in self.nodes:
            self.nodes.append(node)

    # ------------------------------------------------------------------
    def _traverse(self) -> Iterable[GSNNode]:
        # ``nodes`` already contains all diagram nodes, including ones that
        # are not connected yet.  Simply iterate over the list to avoid
        # skipping orphan elements and to maintain a stable drawing order.
        return list(self.nodes)

    # ------------------------------------------------------------------
    def draw(self, canvas, zoom: float = 1.0) -> None:  # pragma: no cover - requires tkinter
        """Render the diagram on a :class:`tkinter.Canvas` instance."""
        # draw connectors first so they appear behind nodes
        for parent in self._traverse():
            for child in parent.children:
                p_pt = (parent.x * zoom, parent.y * zoom)
                c_pt = (child.x * zoom, child.y * zoom)
                if child.node_type in {"Context", "Assumption", "Justification"}:
                    self.drawing_helper.draw_in_context_connection(
                        canvas, p_pt, c_pt
                    )
                else:
                    self.drawing_helper.draw_solved_by_connection(
                        canvas, p_pt, c_pt
                    )
        for node in self._traverse():
            self._draw_node(canvas, node, zoom)

    # ------------------------------------------------------------------
    def _draw_node(self, canvas, node: GSNNode, zoom: float) -> None:  # pragma: no cover - requires tkinter
        x, y = node.x * zoom, node.y * zoom
        scale = 40 * zoom
        typ = node.node_type.lower()
        text = self._format_text(node)
        
        def _call(method, *args, **kwargs):
            try:
                method(*args, **kwargs)
            except TypeError:  # pragma: no cover - fallback for simplified helpers
                kwargs.pop("text", None)
                kwargs.pop("top_text", None)
                kwargs.pop("bottom_text", None)
                method(*args, **kwargs)
        if typ == "solution":
            if node.is_primary_instance:
                _call(
                    self.drawing_helper.draw_solution_shape,
                    canvas,
                    x,
                    y,
                    scale,
                    top_text=node.user_name,
                    bottom_text=node.description,
                    obj_id=node.unique_id,
                )
            else:
                _call(
                    self.drawing_helper.draw_away_solution_shape,
                    canvas,
                    x,
                    y,
                    scale,
                    top_text=node.user_name,
                    bottom_text=node.description,
                    obj_id=node.unique_id,
                )
        elif typ == "goal":
            if node.is_primary_instance:
                _call(
                    self.drawing_helper.draw_goal_shape,
                    canvas,
                    x,
                    y,
                    scale,
                    text=text,
                    obj_id=node.unique_id,
                )
            else:
                _call(
                    self.drawing_helper.draw_away_goal_shape,
                    canvas,
                    x,
                    y,
                    scale,
                    text=text,
                    obj_id=node.unique_id,
                )
        elif typ == "strategy":
            _call(
                self.drawing_helper.draw_strategy_shape,
                canvas,
                x,
                y,
                scale,
                text=text,
                obj_id=node.unique_id,
            )
        elif typ == "assumption":
            _call(
                self.drawing_helper.draw_assumption_shape,
                canvas,
                x,
                y,
                scale,
                text=text,
                obj_id=node.unique_id,
            )
        elif typ == "justification":
            _call(
                self.drawing_helper.draw_justification_shape,
                canvas,
                x,
                y,
                scale,
                text=text,
                obj_id=node.unique_id,
            )
        elif typ == "context":
            _call(
                self.drawing_helper.draw_context_shape,
                canvas,
                x,
                y,
                scale,
                text=text,
                obj_id=node.unique_id,
            )
        elif typ == "module":
            if node.is_primary_instance:
                _call(
                    self.drawing_helper.draw_goal_shape,
                    canvas,
                    x,
                    y,
                    scale,
                    text=text,
                    obj_id=node.unique_id,
                )
            else:
                _call(
                    self.drawing_helper.draw_away_module_shape,
                    canvas,
                    x,
                    y,
                    scale,
                    text=text,
                    obj_id=node.unique_id,
                )

    def _format_text(self, node: GSNNode) -> str:
        """Return node label including description if present."""
        if getattr(node, "description", ""):
            return f"{node.user_name}\n{node.description}"
        return node.user_name
