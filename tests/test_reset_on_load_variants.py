import types
import AutoML
from AutoML import AutoMLApp


def test_reset_on_load_variants(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    app.page_diagram = object()
    app.close_page_diagram = lambda: None
    app.doc_nb = types.SimpleNamespace(
        tabs=lambda: [], event_generate=lambda *a, **k: None, forget=lambda tab: None
    )
    app.diagram_font = types.SimpleNamespace(config=lambda **k: None)
    app.canvas = types.SimpleNamespace(update=lambda: None)
    app.update_views = lambda: None
    app.analysis_tree = types.SimpleNamespace(get_children=lambda: [], delete=lambda *a: None)
    app._undo_stack = []
    app._redo_stack = []
    app.apply_model_data = lambda *a, **k: None
    app.set_last_saved_state = lambda: None
    monkeypatch.setattr(AutoML, "SysMLRepository", types.SimpleNamespace(reset_instance=lambda: None))
    monkeypatch.setattr(AutoML, "AutoMLHelper", lambda: None)
    original = AutoML.AutoML_Helper
    app._reset_on_load_v1()
    app._reset_on_load_v2()
    app._reset_on_load_v3()
    app._reset_on_load_v4()
    AutoML.AutoML_Helper = original
