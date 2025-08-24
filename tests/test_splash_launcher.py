import importlib

from tools.splash_launcher import SplashLauncher


def test_launcher_invokes_main(monkeypatch):
    dummy = importlib.import_module("tests.dummy_module")
    dummy.called["main"] = False

    launcher = SplashLauncher(module_name="tests.dummy_module")
    launcher.launch()

    assert dummy.called["main"] is True
