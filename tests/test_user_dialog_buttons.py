import sys, pathlib, importlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import AutoML as automl
from gui.dialogs.user_info_dialog import UserInfoDialog


def _collect_button_styles(dialog_cls, monkeypatch):
    styles = []
    applied = {"called": 0}

    class DummyButton:
        def __init__(self, master, **kwargs):
            styles.append(kwargs.get("style"))
        def pack(self, *a, **k):
            pass

    class DummyFrame:
        def __init__(self, *a, **k):
            pass
        def pack(self, *a, **k):
            pass

    class DummyDialog:
        def bind(self, *a, **k):
            pass
        ok = lambda self, *a, **k: None
        cancel = lambda self, *a, **k: None

    def fake_apply(style=None):
        applied["called"] += 1

    import gui.mac_button_style as mbs

    module = importlib.import_module(dialog_cls.__module__)
    if hasattr(module, "ttk"):
        monkeypatch.setattr(module.ttk, "Button", DummyButton)
        monkeypatch.setattr(module.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(mbs.ttk, "Button", DummyButton)
    monkeypatch.setattr(mbs.ttk, "Frame", DummyFrame)
    if hasattr(module, "apply_purplish_button_style"):
        monkeypatch.setattr(module, "apply_purplish_button_style", fake_apply)
    monkeypatch.setattr(mbs, "apply_purplish_button_style", fake_apply)

    dlg = DummyDialog()
    dialog_cls.buttonbox(dlg)
    return styles, applied["called"]


def test_user_info_dialog_purplish_buttons(monkeypatch):
    styles, called = _collect_button_styles(UserInfoDialog, monkeypatch)
    assert styles == ["Purple.TButton", "Purple.TButton"]
    assert called == 1


def test_user_select_dialog_purplish_buttons(monkeypatch):
    styles, called = _collect_button_styles(automl.UserSelectDialog, monkeypatch)
    assert styles == ["Purple.TButton", "Purple.TButton"]
    assert called == 1


def test_base_dialog_purplish_buttons(monkeypatch):
    styles, called = _collect_button_styles(automl.simpledialog.Dialog, monkeypatch)
    assert styles == ["Purple.TButton", "Purple.TButton"]
    assert called == 1
