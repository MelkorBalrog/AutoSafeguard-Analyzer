                mal = getattr(self.node, "malfunction", "")
                mode = getattr(self.node, "analysis_mode", getattr(self.app, "diagram_mode", "FTA"))
                if mal and mode != "FTA" and any(
                    getattr(te, "malfunction", "") == mal
                    for te in getattr(self.app, "top_events", [])
                ):
                    self.safety_goal_text.configure(state="disabled")
                    mode = getattr(target_node, "analysis_mode", "FTA")
                    if mode == "CTA":
                        events = getattr(self.app, "cta_events", [])
                    elif mode == "PAA":
                        events = getattr(self.app, "paa_events", [])
                    else:
                        events = self.app.top_events
                    for te in events:
                    if mode in {"CTA", "PAA"} and any(
                        getattr(te, "malfunction", "") == new_mal for te in self.app.top_events
                    ):
                        self.safety_goal_text.configure(state="disabled")
            paa_events.extend(getattr(self, "paa_events", []))
