import sys, types, json
from unittest.mock import MagicMock

# Stub PIL modules for AutoML import
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from AutoML import AutoMLApp
import AutoML


def _no_history_clear_v1(mock):
    return mock.call_count == 0


def _no_history_clear_v2(mock):
    return not mock.called


def _no_history_clear_v3(mock):
    return mock.mock_calls == []


def _no_history_clear_v4(mock):
    mock.assert_not_called()
    return True


def _no_history_clear(mock):
    return _no_history_clear_v3(mock)


def test_load_model_preserves_history(tmp_path, monkeypatch):
    model = tmp_path / "model.json"
    model.write_text("{}")

    app = AutoMLApp.__new__(AutoMLApp)
    app._loaded_model_paths = []
    app.apply_model_data = MagicMock()
    app.set_last_saved_state = MagicMock()
    app._reset_on_load = MagicMock()
    app.has_unsaved_changes = lambda: False

    cuh = MagicMock()
    app.clear_undo_history = cuh

    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", lambda **k: str(model))
    monkeypatch.setattr(AutoML.messagebox, "showerror", lambda *a, **k: None)

    app.load_model()

    assert _no_history_clear(cuh)

