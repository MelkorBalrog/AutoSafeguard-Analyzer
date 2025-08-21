import types
import AutoML
from AutoML import AutoMLApp, AutoML_Helper


def test_load_model_prompts_save(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    app.has_unsaved_changes = lambda: True

    called = {}
    def fake_save_model():
        called['saved'] = True
    app.save_model = fake_save_model

    def fake_askyesnocancel(title, message):
        return True
    monkeypatch.setattr('AutoML.messagebox', types.SimpleNamespace(askyesnocancel=fake_askyesnocancel))
    monkeypatch.setattr('AutoML.filedialog', types.SimpleNamespace(askopenfilename=lambda **kwargs: ''))
    monkeypatch.setattr('AutoML.AutoMLHelper', lambda: object())

    original = AutoML_Helper
    app.load_model()
    AutoML.AutoML_Helper = original
    assert called.get('saved')
