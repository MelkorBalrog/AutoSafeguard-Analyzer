from __future__ import annotations

"""Centralised renderer for AutoML diagrams.

This class acts as a façade over the existing rendering helpers
from :mod:`mainappsrc.automl_core`.  It allows the GUI and tests to
invoke diagram operations through a dedicated object rather than
calling functions directly on the application.
"""

from typing import Any


class DiagramRenderer:
    """Delegate drawing and capture operations for AutoML diagrams."""

    def __init__(self, app: Any) -> None:
        self.app = app

    # Basic node and subtree drawing -------------------------------------------------
    def draw_node(self, *args, **kwargs):
        return self.app.draw_node(*args, **kwargs)

    def draw_subtree(self, *args, **kwargs):
        return self.app.draw_subtree(*args, **kwargs)

    def draw_subtree_with_filter(self, *args, **kwargs):
        return self.app.draw_subtree_with_filter(*args, **kwargs)

    def draw_connections(self, *args, **kwargs):
        return self.app.draw_connections(*args, **kwargs)

    def draw_connections_subtree(self, *args, **kwargs):
        return self.app.draw_connections_subtree(*args, **kwargs)

    def draw_node_on_canvas_pdf(self, *args, **kwargs):
        return self.app.draw_node_on_canvas_pdf(*args, **kwargs)

    def draw_node_on_page_canvas(self, *args, **kwargs):
        return self.app.draw_node_on_page_canvas(*args, **kwargs)

    def draw_page_grid(self, *args, **kwargs):
        return self.app.draw_page_grid(*args, **kwargs)

    def draw_page_nodes_subtree(self, *args, **kwargs):
        return self.app.draw_page_nodes_subtree(*args, **kwargs)

    def draw_page_connections_subtree(self, *args, **kwargs):
        return self.app.draw_page_connections_subtree(*args, **kwargs)

    def draw_page_subtree(self, *args, **kwargs):
        return self.app.draw_page_subtree(*args, **kwargs)

    # Rendering and canvas management ------------------------------------------------
    def render_cause_effect_diagram(self, *args, **kwargs):
        return self.app.render_cause_effect_diagram(*args, **kwargs)

    def redraw_canvas(self, *args, **kwargs):
        return self.app.redraw_canvas(*args, **kwargs)

    def zoom_in(self, *args, **kwargs):
        return self.app.zoom_in(*args, **kwargs)

    def zoom_out(self, *args, **kwargs):
        return self.app.zoom_out(*args, **kwargs)

    def create_diagram_image(self, *args, **kwargs):
        return self.app.create_diagram_image(*args, **kwargs)

    def create_diagram_image_without_grid(self, *args, **kwargs):
        return self.app.create_diagram_image_without_grid(*args, **kwargs)

    def save_diagram_png(self, *args, **kwargs):
        return self.app.save_diagram_png(*args, **kwargs)

    def close_page_diagram(self, *args, **kwargs):
        return self.app.close_page_diagram(*args, **kwargs)

    # Capture helpers ---------------------------------------------------------------
    def capture_event_diagram(self, *args, **kwargs):
        return self.app.capture_event_diagram(*args, **kwargs)

    def capture_page_diagram(self, *args, **kwargs):
        return self.app.capture_page_diagram(*args, **kwargs)

    def capture_diff_diagram(self, *args, **kwargs):
        return self.app.capture_diff_diagram(*args, **kwargs)

    def capture_sysml_diagram(self, *args, **kwargs):
        return self.app.capture_sysml_diagram(*args, **kwargs)

    def capture_cbn_diagram(self, *args, **kwargs):
        return self.app.capture_cbn_diagram(*args, **kwargs)

    def capture_gsn_diagram(self, *args, **kwargs):
        return self.app.capture_gsn_diagram(*args, **kwargs)

    # High-level views --------------------------------------------------------------
    def show_cause_effect_chain(self, *args, **kwargs):
        return self.app.show_cause_effect_chain(*args, **kwargs)

    def show_common_cause_view(self, *args, **kwargs):
        return self.app.show_common_cause_view(*args, **kwargs)
