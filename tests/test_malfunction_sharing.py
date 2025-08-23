import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp


def test_malfunction_shared_across_analyses():
    app = AutoMLApp.__new__(AutoMLApp)
    app.malfunctions = []
    app.top_events = []
    app.cta_events = []
    app.paa_events = []
    app.push_undo_state = lambda: None
    app.update_views = lambda: None
    app.safety_mgmt_toolbox = type("TB", (), {
        "register_created_work_product": lambda *a, **k: None
    })()
    app._update_shared_product_goals = AutoMLApp._update_shared_product_goals.__get__(app, AutoMLApp)

    app.diagram_mode = "FTA"
    app.add_malfunction("M1")
    assert len(app.top_events) == 1

    app.diagram_mode = "PAA"
    app.add_malfunction("M1")
    assert len(app.paa_events) == 1

    assert app.top_events[0].name_readonly
    assert app.paa_events[0].name_readonly
