import sys, types, json, os
from unittest.mock import MagicMock

# Ensure project root is on path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Stub PIL modules for AutoML import
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from AutoML import AutoMLApp
import AutoML


def _app(monkeypatch, tmp_path):
    model = tmp_path / "model.json"
    model.write_text("{}")
    app = AutoMLApp.__new__(AutoMLApp)
    app._loaded_model_paths = []
    app.apply_model_data = MagicMock()
    app.set_last_saved_state = MagicMock()
    app._reset_on_load = MagicMock()
    app.clear_undo_history = MagicMock()
    return app, model


def test_load_model_prompt_cancel(tmp_path, monkeypatch):
    app, model = _app(monkeypatch, tmp_path)
    app.save_model = MagicMock()
    app.has_unsaved_changes = MagicMock(return_value=True)
    open_mock = MagicMock(return_value=str(model))
    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", open_mock)
    monkeypatch.setattr(AutoML.messagebox, "askyesnocancel", lambda *a, **k: None)
    app.load_model()
    open_mock.assert_not_called()
    app._reset_on_load.assert_not_called()


def test_load_model_prompt_no(tmp_path, monkeypatch):
    app, model = _app(monkeypatch, tmp_path)
    app.save_model = MagicMock()
    app.has_unsaved_changes = MagicMock(return_value=True)
    monkeypatch.setattr(AutoML.messagebox, "askyesnocancel", lambda *a, **k: False)
    open_mock = MagicMock(return_value=str(model))
    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", open_mock)
    monkeypatch.setattr(AutoML.messagebox, "showerror", lambda *a, **k: None)
    app.load_model()
    open_mock.assert_called_once()
    app.save_model.assert_not_called()
    app._reset_on_load.assert_called_once()
    app.apply_model_data.assert_called_once_with({})


def test_load_model_prompt_yes(tmp_path, monkeypatch):
    app, model = _app(monkeypatch, tmp_path)
    app.save_model = MagicMock()
    app.has_unsaved_changes = MagicMock(return_value=True)
    monkeypatch.setattr(AutoML.messagebox, "askyesnocancel", lambda *a, **k: True)
    open_mock = MagicMock(return_value=str(model))
    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", open_mock)
    monkeypatch.setattr(AutoML.messagebox, "showerror", lambda *a, **k: None)
    app.load_model()
    app.save_model.assert_called_once()
    open_mock.assert_called_once()
    app._reset_on_load.assert_called_once()
    app.apply_model_data.assert_called_once_with({})


def test_load_model_no_unsaved_changes(tmp_path, monkeypatch):
    app, model = _app(monkeypatch, tmp_path)
    app.save_model = MagicMock()
    app.has_unsaved_changes = MagicMock(return_value=False)
    ask_mock = MagicMock(return_value=False)
    monkeypatch.setattr(AutoML.messagebox, "askyesnocancel", ask_mock)
    open_mock = MagicMock(return_value=str(model))
    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", open_mock)
    monkeypatch.setattr(AutoML.messagebox, "showerror", lambda *a, **k: None)
    app.load_model()
    ask_mock.assert_not_called()
    open_mock.assert_called_once()

