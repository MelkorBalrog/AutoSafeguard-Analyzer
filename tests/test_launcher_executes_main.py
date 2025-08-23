from pathlib import Path
import sys
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import AutoML_Launcher


def test_launcher_runs_automl():
    with mock.patch.object(AutoML_Launcher, "install_best"), \
         mock.patch.object(AutoML_Launcher, "ensure_packages"), \
         mock.patch.object(AutoML_Launcher, "ensure_ghostscript"), \
         mock.patch.object(AutoML_Launcher.memory_manager, "cleanup"), \
         mock.patch.object(AutoML_Launcher.subprocess, "run") as spy:
        AutoML_Launcher.main()
    expected = Path(AutoML_Launcher.__file__).parent / "main" / "AutoML.py"
    spy.assert_called_once()
    args, kwargs = spy.call_args
    assert args[0] == [AutoML_Launcher.sys.executable, str(expected)]
    assert kwargs["cwd"] == Path(AutoML_Launcher.__file__).parent
    assert kwargs["check"] is True
    assert kwargs["env"]["PYTHONPATH"].startswith(str(Path(AutoML_Launcher.__file__).parent))
