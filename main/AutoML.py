                def _update_desc_state():
                    analysis = getattr(self.node, "analysis_mode", getattr(self.app, "diagram_mode", "")).upper()
                    mal = self.mal_var.get().strip() or self.mal_sel_var.get().strip()
                    if analysis in {"CTA", "PAA"} and any(
                        getattr(te, "malfunction", "") == mal for te in self.app.top_events
                    ):
                        self.desc_text.config(state="disabled")
                    else:
                        self.desc_text.config(state="normal")

                    _update_desc_state()

                _update_desc_state()
                    mode = getattr(target_node, "analysis_mode", self.app.diagram_mode)
                    if mode == "CTA":
                        events_iter = getattr(self.app, "cta_events", [])
                    elif mode == "PAA":
                        events_iter = getattr(self.app, "paa_events", [])
                    else:
                        events_iter = self.app.top_events
                    for te in events_iter:
                self.diagram_mode = "FTA"
            combined_paa = list(getattr(self, "paa_events", [])) + [
                te
                for te in getattr(self, "top_events", [])
                te
                for te in getattr(self, "top_events", [])
            if "Prototype Assurance Analysis" in enabled or combined_paa:
                for te in combined_paa:
