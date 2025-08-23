import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp


def test_paa_diagram_has_top_event(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    class DummyCanvas:
        diagram_mode = ""

    def fake_create_tab(mode):
        app.canvas = DummyCanvas()
        app.canvas.diagram_mode = mode
        app.diagram_mode = mode

    app._create_fta_tab = fake_create_tab
    app.top_events = []
    app.cta_events = []
    app.paa_events = []
    app.update_views = lambda: None
    app.open_page_diagram = lambda *a, **k: None
    app.create_paa_diagram()
    assert app.canvas.diagram_mode == "PAA"
    assert app.diagram_mode == "PAA"
    assert len(app.paa_events) == 1
    assert getattr(app.paa_events[0], "is_top_event", False)
