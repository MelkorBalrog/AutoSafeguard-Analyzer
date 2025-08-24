import time
import AutoML_Launcher as launcher


def test_ensure_packages_runs_in_parallel(monkeypatch):
    fake_required = ["pkg1", "pkg2"]
    monkeypatch.setattr(launcher, "REQUIRED_PACKAGES", fake_required)

    def fake_import_module(name):
        raise ImportError

    monkeypatch.setattr(launcher.importlib, "import_module", fake_import_module)

    class FakeProc:
        def __init__(self, *args, **kwargs):
            pass

        def wait(self):
            time.sleep(0.2)

    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *a, **k: FakeProc())
    monkeypatch.setattr(launcher.memory_manager, "register_process", lambda *a, **k: None)
    monkeypatch.setattr(launcher.memory_manager, "cleanup", lambda: None)

    start = time.time()
    launcher.ensure_packages()
    elapsed = time.time() - start
    assert elapsed < 0.35
