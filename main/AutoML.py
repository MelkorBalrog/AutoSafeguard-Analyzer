        all_events = (
            self.app.top_events
            + getattr(self.app, "cta_events", [])
            + getattr(self.app, "paa_events", [])
        )
        self._other_malfunctions = {
            getattr(te, "malfunction", "")
            for te in all_events
            if te is not node and getattr(te, "malfunction", "")
        }
    def _is_malfunction_shared(self, malfunction):
        """Return True if the malfunction is already used by another event."""
        return malfunction in self._other_malfunctions

    def _update_desc_state(self, malfunction):
        state = tk.DISABLED if self._is_malfunction_shared(malfunction) else tk.NORMAL
        if hasattr(self, "safety_goal_text"):
            self.safety_goal_text.config(state=state)



                    self._update_desc_state(self.mal_sel_var.get())

                self._update_desc_state(stored_mal)
                    mode = getattr(target_node, "analysis_mode", "FTA")
                    event_map = {
                        "FTA": self.app.top_events,
                        "CTA": getattr(self.app, "cta_events", []),
                        "PAA": getattr(self.app, "paa_events", []),
                    }
                    for te in event_map.get(mode, self.app.top_events):
            paa_events_dict = {
                te.unique_id: te
                for te in getattr(self, "top_events", [])
            }
            for te in getattr(self, "paa_events", []):
                paa_events_dict.setdefault(te.unique_id, te)
            paa_events = list(paa_events_dict.values())
