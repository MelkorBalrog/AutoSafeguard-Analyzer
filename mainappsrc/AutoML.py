                    events = self.app.get_events_of_same_type(target_node)
                    for te in events:
        for te in self.top_events + getattr(self, "cta_events", []) + getattr(self, "paa_events", []):
    def get_events_of_same_type(self, node) -> list:
        """Return a list of top-level events matching ``node``'s analysis type."""
        if node in self.top_events:
            return self.top_events
        if node in getattr(self, "cta_events", []):
            return getattr(self, "cta_events", [])
        if node in getattr(self, "paa_events", []):
            return getattr(self, "paa_events", [])
        return []

            getattr(te, "malfunction", "") == name
            for te in self.top_events
            + getattr(self, "cta_events", [])
            + getattr(self, "paa_events", [])
