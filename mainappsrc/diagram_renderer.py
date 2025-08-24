from __future__ import annotations

from typing import Any, Iterable


class DiagramRenderer:
    """Thin wrapper around diagram-related methods.

    This helper delegates to the original :mod:`AutoML` implementation so that
    rendering logic can be accessed through a dedicated object.  Future refactors
    can progressively move functionality here without touching call sites.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    def draw_node(self, node: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_node(node)

    def draw_subtree_with_filter(self, canvas: Any, root_event: Any,
                                 visible_nodes: Iterable[Any]) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_subtree_with_filter(canvas, root_event, visible_nodes)

    def draw_subtree(self, canvas: Any, root_event: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_subtree(canvas, root_event)

    def draw_connections(self, node: Any, drawn_ids: set | None = None) -> Any:  # pragma: no cover - UI routine
        if drawn_ids is None:
            drawn_ids = set()
        return self.app.draw_connections(node, drawn_ids)

    def draw_connections_subtree(self, canvas: Any, node: Any, drawn_ids: set) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_connections_subtree(canvas, node, drawn_ids)

    def draw_node_on_canvas_pdf(self, canvas: Any, node: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_node_on_canvas_pdf(canvas, node)

    def draw_node_on_page_canvas(self, canvas: Any, node: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_node_on_page_canvas(canvas, node)

    def draw_page_grid(self) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_page_grid()

    def draw_page_nodes_subtree(self, node: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_page_nodes_subtree(node)

    def draw_page_connections_subtree(self, node: Any, visited_ids: set) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_page_connections_subtree(node, visited_ids)

    def draw_page_subtree(self, page_root: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.draw_page_subtree(page_root)

    def render_cause_effect_diagram(self, row: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.render_cause_effect_diagram(row)

    def redraw_canvas(self) -> Any:  # pragma: no cover - UI routine
        return self.app.redraw_canvas()

    def zoom_in(self) -> Any:  # pragma: no cover - UI routine
        return self.app.zoom_in()

    def zoom_out(self) -> Any:  # pragma: no cover - UI routine
        return self.app.zoom_out()

    def create_diagram_image(self) -> Any:  # pragma: no cover - UI routine
        return self.app.create_diagram_image()

    def create_diagram_image_without_grid(self) -> Any:  # pragma: no cover - UI routine
        return self.app.create_diagram_image_without_grid()

    def save_diagram_png(self) -> Any:  # pragma: no cover - UI routine
        return self.app.save_diagram_png()

    def close_page_diagram(self) -> Any:  # pragma: no cover - UI routine
        return self.app.close_page_diagram()

    def capture_event_diagram(self, event: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.capture_event_diagram(event)

    def capture_page_diagram(self, page_node: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.capture_page_diagram(page_node)

    def capture_diff_diagram(self, top_event: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.capture_diff_diagram(top_event)

    def capture_sysml_diagram(self, diagram: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.capture_sysml_diagram(diagram)

    def capture_cbn_diagram(self, doc: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.capture_cbn_diagram(doc)

    def capture_gsn_diagram(self, diagram: Any) -> Any:  # pragma: no cover - UI routine
        return self.app.capture_gsn_diagram(diagram)

    def show_cause_effect_chain(self) -> Any:  # pragma: no cover - UI routine
        return self.app.show_cause_effect_chain()

    def show_common_cause_view(self) -> Any:  # pragma: no cover - UI routine
        return self.app.show_common_cause_view()
