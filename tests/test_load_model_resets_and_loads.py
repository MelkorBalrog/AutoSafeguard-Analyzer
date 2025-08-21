import json
import types
import AutoML
from AutoML import AutoMLApp

def test_load_model_resets_and_loads(monkeypatch, tmp_path):
    app = AutoMLApp.__new__(AutoMLApp)
    app.has_unsaved_changes = lambda: False
    app._loaded_model_paths = []

    data = {"top_events": []}
    path = tmp_path / "model.json"
    path.write_text(json.dumps(data))

    loaded = {}
    def fake_apply(d, ensure_root=True):
        loaded.update(d)
    app.apply_model_data = fake_apply
    app.set_last_saved_state = lambda: None

    reset_called = {}
    def fake_reset():
        reset_called["called"] = True
    app._reset_on_load_v4 = fake_reset

    monkeypatch.setattr('AutoML.filedialog', types.SimpleNamespace(askopenfilename=lambda **k: str(path)))

    app.load_model()

    assert reset_called.get("called")
    assert loaded == data
    assert app._loaded_model_paths == [str(path)]
