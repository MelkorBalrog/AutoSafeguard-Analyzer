import importlib

def test_dark_mode_background(monkeypatch):
    monkeypatch.setenv('AUTOML_STYLE', 'dark')
    import gui.style_manager as sm
    importlib.reload(sm)
    mgr = sm.StyleManager.get_instance()
    assert mgr.background == '#000000'
    assert mgr.get_color('Actor') == '#90CAF9'
