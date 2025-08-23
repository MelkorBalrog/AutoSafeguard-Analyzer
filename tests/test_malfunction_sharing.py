from main.AutoML import AutoMLApp, FaultTreeNode


def test_malfunction_shared_across_modes_allowed():
    app = AutoMLApp.__new__(AutoMLApp)
    fta = FaultTreeNode("", "TOP EVENT")
    fta.analysis_mode = "FTA"
    fta.malfunction = "M1"
    cta = FaultTreeNode("", "TOP EVENT")
    cta.analysis_mode = "CTA"
    app.top_events = [fta]
    app.cta_events = [cta]
    app.paa_events = []

    mode = getattr(cta, "analysis_mode", "FTA")
    event_map = {
        "FTA": app.top_events,
        "CTA": getattr(app, "cta_events", []),
        "PAA": getattr(app, "paa_events", []),
    }
    conflict = any(
        te is not cta and getattr(te, "malfunction", "") == "M1"
        for te in event_map.get(mode, app.top_events)
    )
    assert not conflict
