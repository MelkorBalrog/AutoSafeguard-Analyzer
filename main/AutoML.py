
                def _check_shared(mal):
                    all_events = (
                        self.app.top_events
                        + getattr(self.app, "cta_events", [])
                        + getattr(self.app, "paa_events", [])
                    )
                    shared = any(
                        te is not self.node and getattr(te, "malfunction", "") == mal
                        for te in all_events
                    )
                    self.safety_goal_text.config(state=tk.DISABLED if shared else tk.NORMAL)


                    _check_shared(self.mal_sel_var.get())

                _check_shared(stored_mal)
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
