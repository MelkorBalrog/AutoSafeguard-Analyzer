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
