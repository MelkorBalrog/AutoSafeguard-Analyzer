            ] + list(getattr(self, "paa_events", []))
                seen_ids = set()
                    if te.unique_id in seen_ids:
                        continue
                    seen_ids.add(te.unique_id)
