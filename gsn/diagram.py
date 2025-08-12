"""Simple rendering support for GSN diagrams."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Set
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

    # ------------------------------------------------------------------
    def _traverse(self) -> Iterable[GSNNode]:
        visited: Set[str] = set()

        def rec(node: GSNNode):
            if node.unique_id in visited:
                return
            visited.add(node.unique_id)
            yield node
            for child in node.children:
                yield from rec(child)

        yield from rec(self.root)

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
        if typ == "solution":
            if node.is_primary_instance:
                self.drawing_helper.draw_solution_shape(
                    canvas, x, y, scale, obj_id=node.unique_id
                )
            else:
                self.drawing_helper.draw_away_solution_shape(
                    canvas, x, y, scale, obj_id=node.unique_id
                )
        elif typ == "goal":
            if node.is_primary_instance:
                self.drawing_helper.draw_goal_shape(
                    canvas, x, y, scale, obj_id=node.unique_id
                )
            else:
                self.drawing_helper.draw_away_goal_shape(
                    canvas, x, y, scale, obj_id=node.unique_id
                )
        elif typ == "strategy":
            self.drawing_helper.draw_strategy_shape(
                canvas, x, y, scale, obj_id=node.unique_id
            )
        elif typ == "assumption":
            self.drawing_helper.draw_assumption_shape(
                canvas, x, y, scale, obj_id=node.unique_id
            )
        elif typ == "justification":
            self.drawing_helper.draw_justification_shape(
                canvas, x, y, scale, obj_id=node.unique_id
            )
        elif typ == "context":
            self.drawing_helper.draw_context_shape(
                canvas, x, y, scale, obj_id=node.unique_id
            )
        elif typ == "module":
            if node.is_primary_instance:
                self.drawing_helper.draw_goal_shape(
                    canvas, x, y, scale, obj_id=node.unique_id
                )
            else:
                self.drawing_helper.draw_away_module_shape(
                    canvas, x, y, scale, obj_id=node.unique_id
                )
