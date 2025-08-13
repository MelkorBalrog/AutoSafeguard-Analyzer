"""Simple rendering support for GSN diagrams."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List
import uuid

import tkinter.font as tkFont

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
    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation of this diagram."""
        return {
            "diag_id": self.diag_id,
            "root": self.root.unique_id,
            "nodes": [n.to_dict() for n in self.nodes],
        }

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> "GSNDiagram":
        """Reconstruct a :class:`GSNDiagram` from *data*."""
        node_map: dict[str, GSNNode] = {}
        for nd in data.get("nodes", []):
            GSNNode.from_dict(nd, nodes=node_map)
        GSNNode.resolve_references(node_map)
        root_id = data.get("root")
        root = node_map.get(root_id)
        diag = cls(root, diag_id=data.get("diag_id", str(uuid.uuid4())))
        diag.nodes = list(node_map.values())
        return diag

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
        typ = node.node_type.lower()
        text = self._format_text(node)

        try:
            font_obj = tkFont.Font(family="Arial", size=max(int(10 * zoom), 1))
            width, height = self.drawing_helper.get_text_size(text, font_obj)
        except Exception:  # pragma: no cover - headless fallback
            font_obj = None
            width = height = 0
        padding = 10 * zoom
        base_scale = 60 * zoom

        def _call(method, *args, **kwargs):
            try:
                method(*args, **kwargs)
            except TypeError:  # pragma: no cover - fallback for simplified helpers
                kwargs.pop("text", None)
                kwargs.pop("top_text", None)
                kwargs.pop("bottom_text", None)
                kwargs.pop("font_obj", None)
                method(*args, **kwargs)

        if typ == "solution":
            text = self._format_text(node)
            t_width, t_height = self.drawing_helper.get_text_size(text, font_obj)
            radius = max(
                base_scale / 2,
                t_width / 2 + padding,
                t_height / 2 + padding,
            )
            scale = radius * 2
            draw_func = (
                self.drawing_helper.draw_solution_shape
                if node.is_primary_instance
                else self.drawing_helper.draw_away_solution_shape
            )
            _call(
                draw_func,
                canvas,
                x,
                y,
                scale,
                text=text,
                font_obj=font_obj,
                obj_id=node.unique_id,
            )
        elif typ in {"goal", "module"}:
            ratio = 0.6
            scale = max(base_scale, width + padding, (height + padding) / ratio)
            if typ == "goal":
                draw_func = (
                    self.drawing_helper.draw_goal_shape
                    if node.is_primary_instance
                    else self.drawing_helper.draw_away_goal_shape
                )
            else:  # module
                draw_func = (
                    self.drawing_helper.draw_goal_shape
                    if node.is_primary_instance
                    else self.drawing_helper.draw_away_module_shape
                )
            _call(
                draw_func,
                canvas,
                x,
                y,
                scale,
                text=text,
                font_obj=font_obj,
                obj_id=node.unique_id,
            )
        elif typ == "strategy":
            ratio = 0.5
            scale = max(base_scale, width + padding, (height + padding) / ratio)
            _call(
                self.drawing_helper.draw_strategy_shape,
                canvas,
                x,
                y,
                scale,
                text=text,
                font_obj=font_obj,
                obj_id=node.unique_id,
            )
        elif typ in {"assumption", "justification", "context"}:
            ratio = 0.5
            scale = max(base_scale, width + padding, (height + padding) / ratio)
            draw_map = {
                "assumption": self.drawing_helper.draw_assumption_shape,
                "justification": self.drawing_helper.draw_justification_shape,
                "context": self.drawing_helper.draw_context_shape,
            }
            _call(
                draw_map[typ],
                canvas,
                x,
                y,
                scale,
                text=text,
                font_obj=font_obj,
                obj_id=node.unique_id,
            )

    def _format_text(self, node: GSNNode) -> str:
        """Return node label including description if present."""
        if node.node_type == "Solution":
            lines = [node.user_name]
            if getattr(node, "spi_target", ""):
                lines.append(f"SPI: {node.spi_target}")
            if getattr(node, "description", ""):
                lines.append(node.description)
            return "\n".join(lines)
        if getattr(node, "description", ""):
            return f"{node.user_name}\n{node.description}"
        return node.user_name
