                    events = []
                    if target_node in self.app.top_events:
                        events = self.app.top_events
                    elif target_node in getattr(self.app, "cta_events", []):
                        events = getattr(self.app, "cta_events", [])
                    elif target_node in getattr(self.app, "paa_events", []):
                        events = getattr(self.app, "paa_events", [])
                    for te in events:
