import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp


def test_pra_diagram_has_top_event(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    class DummyCanvas:
        mode = ""
    def fake_create_tab():
        app.canvas = DummyCanvas()
    app._create_fta_tab = fake_create_tab
    app.top_events = []
    app.update_views = lambda: None
    app.create_pra_diagram()
    assert app.canvas.mode == "PRA"
    assert len(app.top_events) == 1
    assert getattr(app.top_events[0], "is_top_event", False)
    assert getattr(app.top_events[0], "analysis_mode", "") == "PRA"
