import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from gui import messagebox as mb


def test_askyesno_uses_custom_dialog(monkeypatch):
    called = {}
    def fake_dialog(title, message, buttons):
        called['buttons'] = buttons
        return True
    monkeypatch.setattr(mb, '_create_dialog', fake_dialog)
    assert mb.askyesno('Title', 'Message') is True
    assert called['buttons'] == [('Yes', True), ('No', False)]


def test_askyesnocancel_uses_custom_dialog(monkeypatch):
    def fake_dialog(title, message, buttons):
        assert buttons == [('Yes', True), ('No', False), ('Cancel', None)]
        return None
    monkeypatch.setattr(mb, '_create_dialog', fake_dialog)
    assert mb.askyesnocancel('Title', 'Message') is None


def test_askokcancel_uses_custom_dialog(monkeypatch):
    def fake_dialog(title, message, buttons):
        assert buttons == [('OK', True), ('Cancel', False)]
        return False
    monkeypatch.setattr(mb, '_create_dialog', fake_dialog)
    assert mb.askokcancel('Title', 'Message') is False


def test_create_dialog_uses_purple_button_style(monkeypatch):
    colors = []

    class DummyButton:
        def __init__(self, master, **kwargs):
            kwargs.setdefault("bg", "#f3eaff")
            kwargs.setdefault("hover_bg", "#e6d9ff")
            colors.append((kwargs.get("bg"), kwargs.get("hover_bg")))

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

    class DummyDialog:
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

        def geometry(self, *a, **k):
            pass

        def update_idletasks(self):
            pass

        def attributes(self, *a, **k):
            pass

        def lift(self, *a, **k):
            pass

        def winfo_screenwidth(self):
            return 1000

        def winfo_screenheight(self):
            return 800

        def destroy(self):
            pass

        def protocol(self, *a, **k):
            pass

        def wait_window(self):
            pass

    monkeypatch.setattr(mb, "PurpleButton", DummyButton)
    monkeypatch.setattr(mb.ttk, "Frame", lambda *a, **k: DummyFrame())
    monkeypatch.setattr(mb.ttk, "Label", lambda *a, **k: DummyLabel())
    monkeypatch.setattr(mb.ttk, "Style", lambda *a, **k: type("S", (), {"configure": lambda *a, **k: None})())
    monkeypatch.setattr(mb.tk, "Toplevel", lambda root: DummyDialog(root))
    monkeypatch.setattr(mb.tk, "_default_root", None)
    monkeypatch.setattr(
        mb.tk,
        "Tk",
        lambda: type("Root", (), {"withdraw": lambda self: None, "destroy": lambda self: None})(),
    )

    mb._create_dialog("Title", "Message", [("OK", True)])
    assert colors == [("#f3eaff", "#e6d9ff")]


def test_create_dialog_applies_light_blue_background(monkeypatch):
    calls = []

    class DummyFrame:
        def __init__(self, *a, **k):
            calls.append(k.get("style"))

        def pack(self, *a, **k):
            pass

    class DummyLabel:
        def __init__(self, *a, **k):
            calls.append(k.get("style"))

        def pack(self, *a, **k):
            pass

    class DummyDialog:
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

        def geometry(self, *a, **k):
            pass

        def update_idletasks(self):
            pass

        def attributes(self, *a, **k):
            pass

        def lift(self, *a, **k):
            pass

        def winfo_screenwidth(self):
            return 1000

        def winfo_screenheight(self):
            return 800

        def destroy(self):
            pass

        def protocol(self, *a, **k):
            pass

        def wait_window(self):
            pass

    class DummyStyle:
        def __init__(self, master=None):
            pass

        def configure(self, name, **kw):
            calls.append((name, kw))

    monkeypatch.setattr(mb.tk, "_default_root", None)
    monkeypatch.setattr(
        mb.tk,
        "Tk",
        lambda: type("Root", (), {"withdraw": lambda self: None, "destroy": lambda self: None})(),
    )
    monkeypatch.setattr(mb.tk, "Toplevel", lambda root: DummyDialog(root))
    monkeypatch.setattr(mb.ttk, "Frame", lambda *a, **k: DummyFrame(*a, **k))
    monkeypatch.setattr(mb.ttk, "Label", lambda *a, **k: DummyLabel(*a, **k))
    monkeypatch.setattr(mb.ttk, "Style", DummyStyle)
    monkeypatch.setattr(
        mb,
        "PurpleButton",
        lambda *a, **k: type("DummyButton", (), {"pack": lambda *a, **k: None})(),
    )

    mb._create_dialog("Title", "Message", [("OK", True)])
    assert ("Dialog.TFrame", {"background": mb.LIGHT_BLUE}) in calls
    assert ("Dialog.TLabel", {"background": mb.LIGHT_BLUE}) in calls


def test_create_dialog_keeps_existing_root(monkeypatch):
    class DummyRoot:
        def __init__(self):
            self.withdrawn = False

        def withdraw(self):
            self.withdrawn = True

    dummy_root = DummyRoot()
    monkeypatch.setattr(mb.tk, "_default_root", dummy_root)

    class DummyDialog:
        def __init__(self, root):
            self.protocol = lambda *a, **k: None

        def title(self, *a, **k):
            pass

        def resizable(self, *a, **k):
            pass

        def transient(self, *a, **k):
            pass

        def grab_set(self):
            pass

        def geometry(self, *a, **k):
            pass

        def update_idletasks(self):
            pass

        def attributes(self, *a, **k):
            pass

        def lift(self, *a, **k):
            pass

        def winfo_screenwidth(self):
            return 1000

        def winfo_screenheight(self):
            return 800

        def destroy(self):
            pass

        def protocol(self, *a, **k):
            pass

        def wait_window(self):
            pass

    monkeypatch.setattr(mb.tk, "Toplevel", lambda root: DummyDialog(root))
    monkeypatch.setattr(mb.ttk, "Frame", lambda *a, **k: type("F", (), {"pack": lambda *a, **k: None})())
    monkeypatch.setattr(mb.ttk, "Label", lambda *a, **k: type("L", (), {"pack": lambda *a, **k: None})())
    monkeypatch.setattr(mb.ttk, "Style", lambda *a, **k: type("S", (), {"configure": lambda *a, **k: None})())
    monkeypatch.setattr(mb, "PurpleButton", lambda *a, **k: type("B", (), {"pack": lambda *a, **k: None})())

    mb._create_dialog("Title", "Message", [("OK", True)])
    assert dummy_root.withdrawn is False
