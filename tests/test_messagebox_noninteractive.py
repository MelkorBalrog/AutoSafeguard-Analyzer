from gui.controls import messagebox


def test_showinfo_does_not_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):  # pragma: no cover - simple flag setter
        nonlocal called
        called = True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    messagebox.showinfo("T", "M")
    assert called is False


def test_showwarning_does_not_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):  # pragma: no cover - simple flag setter
        nonlocal called
        called = True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    messagebox.showwarning("T", "M")
    assert called is False


def test_showerror_does_not_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):  # pragma: no cover - simple flag setter
        nonlocal called
        called = True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    messagebox.showerror("T", "M")
    assert called is False


def test_askyesno_displays_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    assert messagebox.askyesno("T", "M") is True
    assert called is True
