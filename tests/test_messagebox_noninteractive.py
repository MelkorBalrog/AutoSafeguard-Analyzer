from gui import messagebox


def _was_called(monkeypatch, func_name):
    called = False

    def fake(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(messagebox.tk_messagebox, func_name, fake)
    getattr(messagebox, func_name)("T", "M")
    return called


def test_showinfo_does_not_popup(monkeypatch):
    assert _was_called(monkeypatch, "showinfo") is False


def test_showwarning_does_not_popup(monkeypatch):
    assert _was_called(monkeypatch, "showwarning") is False


def test_showerror_does_not_popup(monkeypatch):
    assert _was_called(monkeypatch, "showerror") is False


def test_askyesno_displays_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr(messagebox.tk_messagebox, "askyesno", fake)
    assert messagebox.askyesno("T", "M") is True
    assert called is True
