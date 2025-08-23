                self.ensure_fta_tab("FTA")
                self.ensure_fta_tab("CTA")
                self.ensure_fta_tab("PAA")
    def ensure_fta_tab(self, mode: str | None = None):
        """Recreate the analysis tab for the given diagram mode if closed."""
        mode = mode or getattr(self, "diagram_mode", "FTA")
            self.canvas.diagram_mode = mode
            self.diagram_mode = mode
            self.doc_nb.select(self.canvas_tab)
            self._update_analysis_menus()
        self.ensure_fta_tab(getattr(self, "diagram_mode", "FTA"))
