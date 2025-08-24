import sys
from pathlib import Path
import types

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mainappsrc.AutoML import AutoMLApp

def test_malfunction_shared_across_event_types():
    app = AutoMLApp.__new__(AutoMLApp)
    fta = types.SimpleNamespace(malfunction="M1")
    cta = types.SimpleNamespace(malfunction="")
    app.top_events = [fta]
    app.cta_events = [cta]
    app.paa_events = []
    events = app.get_events_of_same_type(cta)
    assert fta not in events
    assert not any(te is not cta and getattr(te, "malfunction", "") == "M1" for te in events)

def test_malfunction_unique_within_same_type():
    app = AutoMLApp.__new__(AutoMLApp)
    cta1 = types.SimpleNamespace(malfunction="M1")
    cta2 = types.SimpleNamespace(malfunction="")
    app.top_events = []
    app.cta_events = [cta1, cta2]
    app.paa_events = []
    events = app.get_events_of_same_type(cta2)
    assert any(te is not cta2 and getattr(te, "malfunction", "") == "M1" for te in events)
