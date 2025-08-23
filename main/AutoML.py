import os
import sys

# Ensure repository root is on sys.path for intra-package imports
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

        mode = getattr(self, "diagram_mode", "FTA")
        event_lists = {
            "FTA": self.top_events,
            "CTA": getattr(self, "cta_events", []),
            "PAA": getattr(self, "paa_events", []),
        }
        events = event_lists.get(mode, self.top_events)

        if not any(getattr(te, "malfunction", "") == name for te in events):
            if len(events) == 1 and not getattr(events[0], "malfunction", ""):
                events[0].malfunction = name
                self.root_node = events[0]
            legacy_paas = [
                if getattr(te, "analysis_mode", "") == "PAA"
            paa_events = list(getattr(self, "paa_events", [])) + legacy_paas
                if getattr(te, "analysis_mode", "") != "PAA"
            cta_events = list(getattr(self, "cta_events", []))
            if "CTA" in enabled or cta_events:
                for idx, te in enumerate(cta_events):
        mode = getattr(self, "diagram_mode", "FTA")
        if mode == "CTA":
            self.cta_events.append(new_event)
            self.cta_root_node = new_event
            analysis = "CTA"
        elif mode == "PAA":
            self.paa_events.append(new_event)
            self.paa_root_node = new_event
            analysis = "Prototype Assurance Analysis"
        else:
            self.top_events.append(new_event)
            self.fta_root_node = new_event
            analysis = "FTA"
        self._update_shared_product_goals()
