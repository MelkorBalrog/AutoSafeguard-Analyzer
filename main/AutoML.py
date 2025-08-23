                if self.app.is_malfunction_shared_across_analyses(self.node):
                    self.safety_goal_text.config(state="disabled")
                if new_mal and self.app.is_duplicate_malfunction(target_node, new_mal):
                    messagebox.showerror(
                        "Duplicate Malfunction",
                        "This malfunction is already assigned to another top level event of the same analysis.",
                    )
                    new_mal = getattr(self.node, "malfunction", "")
                    self.mal_sel_var.set(new_mal)
    def is_duplicate_malfunction(self, node, name: str) -> bool:
        """Return True if ``name`` is used by another top event of the same analysis type."""
        if not name:
            return False
        if node in getattr(self, "cta_events", []):
            events = getattr(self, "cta_events", [])
        elif node in getattr(self, "paa_events", []):
            events = getattr(self, "paa_events", [])
        else:
            events = self.top_events
        return any(te is not node and getattr(te, "malfunction", "") == name for te in events)

    def is_malfunction_shared_across_analyses(self, node) -> bool:
        """Return True if the node's malfunction is used in more than one analysis."""
        name = getattr(node, "malfunction", "")
        if not name:
            return False
        events = self.top_events + getattr(self, "cta_events", []) + getattr(self, "paa_events", [])
        count = sum(1 for te in events if getattr(te, "malfunction", "") == name)
        return count > 1

                self.diagram_mode = "FTA"
            if "Prototype Assurance Analysis" in enabled or paa_events or getattr(self, "paa_events", []):
                all_paa = list(paa_events)
                for te in getattr(self, "paa_events", []):
                    if te not in all_paa:
                        all_paa.append(te)
                for te in all_paa:
                for te in getattr(self, "cta_events", []):
