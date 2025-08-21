import os
import sys
import types
from unittest.mock import MagicMock

# Stub PIL modules for AutoML import
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp
import AutoML


def test_load_model_cancel(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    app._loaded_model_paths = []
    app._reset_on_load = MagicMock()
    app.apply_model_data = MagicMock()
    app.set_last_saved_state = MagicMock()
    monkeypatch.setattr(app, "has_unsaved_changes", lambda: True)
    askopen = MagicMock()
    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", askopen)
    app._prompt_save_before_load = lambda: None
    app.load_model()
    askopen.assert_not_called()
    app._reset_on_load.assert_not_called()


def test_load_model_no_save(monkeypatch, tmp_path):
    model = tmp_path / "model.json"
    model.write_text("{}")
    app = AutoMLApp.__new__(AutoMLApp)
    app._loaded_model_paths = []
    app._reset_on_load = MagicMock()
    app.apply_model_data = MagicMock()
    app.set_last_saved_state = MagicMock()
    app.save_model = MagicMock()
    monkeypatch.setattr(app, "has_unsaved_changes", lambda: True)
    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", lambda **k: str(model))
    app._prompt_save_before_load = lambda: False
    app.load_model()
    app.save_model.assert_not_called()
    app._reset_on_load.assert_called_once()
