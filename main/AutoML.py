            paa_events_dict = {
                te.unique_id: te
                for te in getattr(self, "top_events", [])
            }
            for te in getattr(self, "paa_events", []):
                paa_events_dict.setdefault(getattr(te, "unique_id", id(te)), te)
            paa_events = list(paa_events_dict.values())
