        # When a malfunction is shared across different analysis types the
        # description becomes read-only and must be edited through the product
        # goals editor.
        self._lock_desc_if_shared()

                    self._lock_desc_if_shared()
    def _lock_desc_if_shared(self):
        """Disable description editing if malfunction is shared across analyses."""
        if getattr(self.node, "node_type", "").upper() != "TOP EVENT":
            return
        mal = self.mal_var.get().strip() if hasattr(self, "mal_var") else ""
        if not mal:
            mal = getattr(self.node, "malfunction", "")
        all_events = list(getattr(self.app, "top_events", []))
        all_events += list(getattr(self.app, "cta_events", []))
        all_events += list(getattr(self.app, "paa_events", []))
        other = next(
            (
                te
                for te in all_events
                if te is not self.node and getattr(te, "malfunction", "") == mal
            ),
            None,
        )
        if other and getattr(other, "analysis_mode", "FTA") != getattr(
            self.node, "analysis_mode", getattr(self.app, "diagram_mode", "FTA")
        ):
            self.desc_text.config(state=tk.DISABLED)
        else:
            self.desc_text.config(state=tk.NORMAL)

                    events_by_mode = {
                        "FTA": getattr(self.app, "top_events", []),
                        "CTA": getattr(self.app, "cta_events", []),
                        "PAA": getattr(self.app, "paa_events", []),
                    }
                    mode = getattr(target_node, "analysis_mode", getattr(self.app, "diagram_mode", "FTA"))
                    duplicates = events_by_mode.get(mode, [])
                    for te in duplicates:
                    else:
                        all_events = sum(events_by_mode.values(), [])
                        other = next(
                            (
                                te
                                for te in all_events
                                if te is not target_node and getattr(te, "malfunction", "") == new_mal
                            ),
                            None,
                        )
                        if other:
                            target_node.description = other.description
                            self.desc_text.config(state=tk.DISABLED)
                # Explicitly set diagram mode to FTA before opening the page.
                self.diagram_mode = "FTA"
            # ``paa_events`` historically lived in ``self.paa_events``.  Merge any
            # still stored there to avoid inserting a duplicate "PAAs" group.
            paa_events.extend(getattr(self, "paa_events", []))

