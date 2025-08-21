import sys, types
from unittest.mock import MagicMock

# Stub PIL modules for AutoML import
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from AutoML import AutoMLApp
import AutoML


class DummyNotebook:
    def __init__(self):
        self._tabs = ["t1", "t2"]

    def tabs(self):
        return list(self._tabs)

    def event_generate(self, _):
        pass

    def forget(self, tab_id):
        if tab_id in self._tabs:
            self._tabs.remove(tab_id)


def _new_model_app(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    app.doc_nb = DummyNotebook()
    app.analysis_tree = MagicMock()
    app.analysis_tree.get_children.return_value = []
    app.analysis_tree.delete = MagicMock()
    app.apply_model_data = MagicMock()
    app.set_last_saved_state = MagicMock()
    app.update_views = MagicMock()
    app.close_page_diagram = MagicMock()
    app.page_diagram = object()
    app.has_unsaved_changes = lambda: False
    app.save_model = MagicMock()
    app._undo_stack = []
    app._redo_stack = []
    app.zoom = 1.0
    app.diagram_font = MagicMock()
    app.diagram_font.config = MagicMock()

    monkeypatch.setattr(AutoML, "SysMLRepository", MagicMock())
    monkeypatch.setattr(AutoML, "AutoMLHelper", MagicMock())
    monkeypatch.setattr(AutoML, "AutoML_Helper", MagicMock(), raising=False)
    monkeypatch.setattr(AutoML, "update_probability_tables", lambda *a, **k: None)
    return app


def test_new_model_does_not_create_fta_tab(monkeypatch):
    app = _new_model_app(monkeypatch)

    def fake_create_tab():
        app.canvas = MagicMock()

    app._create_fta_tab = MagicMock(side_effect=fake_create_tab)
    app.new_model()
    app._create_fta_tab.assert_not_called()
    assert app.doc_nb.tabs() == []


def test_reset_on_load_does_not_create_fta_tab(monkeypatch):
    app = _new_model_app(monkeypatch)
    app._create_fta_tab = MagicMock()
    app._reset_on_load()
    app._create_fta_tab.assert_not_called()
