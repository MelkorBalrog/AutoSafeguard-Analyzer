            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
            fill = self.get_node_fill_color(n, getattr(canvas, "diagram_mode", None))
        fill_color = self.get_node_fill_color(node, getattr(canvas, "diagram_mode", None))
            node_color = self.get_node_fill_color(node, getattr(canvas, "diagram_mode", None))
    def get_node_fill_color(self, node, mode: str | None = None):
        """Return the fill color for *node* based on analysis mode.

        Parameters
        ----------
        node: FaultTreeNode | None
            Unused but kept for API compatibility.
        mode: str | None
            Explicit diagram mode to use.  Falls back to the currently
            focused canvas' ``diagram_mode`` when ``None``.
        """

        diagram_mode = mode or getattr(getattr(self, "canvas", None), "diagram_mode", "FTA")
        if diagram_mode == "CTA":
        if diagram_mode == "PAA":
        # Determine the fill color using the active canvas' mode
        fill_color = self.get_node_fill_color(node, getattr(self.canvas, "diagram_mode", None))
        # Redraw the active canvas so node colors reflect the selected tab
        self.redraw_canvas()
        fill_color = self.get_node_fill_color(node, getattr(canvas, "diagram_mode", None))
        fill_color = self.app.get_node_fill_color(node, getattr(self.canvas, "diagram_mode", None))
