import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from gui import messagebox


def test_messagebox_buttons_use_purple_style(monkeypatch):
    styles = []

    class DummyBtn:
        def __init__(self, master, *, text='', style='', command=None):
            styles.append(style)
            self.command = command
        def pack(self, *a, **k):
            pass

    class DummyFrame:
        def __init__(self, *a, **k):
            pass
        def pack(self, *a, **k):
            pass

    class DummyLabel:
        def __init__(self, *a, **k):
            pass
        def pack(self, *a, **k):
            pass

    class DummyTop:
        def __init__(self, root):
            pass
        def title(self, *a):
            pass
        def resizable(self, *a, **k):
            pass
        def transient(self, *a, **k):
            pass
        def grab_set(self):
            pass
        def destroy(self):
            pass
        def protocol(self, *a, **k):
            pass
        def wait_window(self):
            pass

    monkeypatch.setattr(messagebox.tk, "_default_root", object())
    monkeypatch.setattr(messagebox.tk, "Toplevel", lambda root: DummyTop(root))
    monkeypatch.setattr(messagebox.ttk, "Frame", lambda *a, **k: DummyFrame())
    monkeypatch.setattr(messagebox.ttk, "Label", lambda *a, **k: DummyLabel())
    monkeypatch.setattr(messagebox.ttk, "Button", DummyBtn)
    monkeypatch.setattr(messagebox, "apply_purplish_button_style", lambda: None)
    messagebox._create_dialog("t", "m", [("OK", True)])
    assert styles == ["Purple.TButton"]
