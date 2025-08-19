from gui import messagebox
import tkinter.messagebox as tk_messagebox


def test_showinfo_invokes_tk(monkeypatch):
    calls = {}

    def fake_showinfo(title, message, **options):
        calls['args'] = (title, message)
        return 'ok'

    monkeypatch.setattr(tk_messagebox, 'showinfo', fake_showinfo)
    monkeypatch.setattr(messagebox.logger, 'log_message', lambda *a, **k: None)
    monkeypatch.setattr(messagebox.logger, 'show_temporarily', lambda: None)

    messagebox.showinfo('Title', 'Message')

    assert calls['args'] == ('Title', 'Message')
