from pathlib import Path
import runpy
import AutoML_Launcher


def test_launcher_runs_automl(mocker):
    mocker.patch.object(AutoML_Launcher, "install_best")
    mocker.patch.object(AutoML_Launcher, "ensure_packages")
    mocker.patch.object(AutoML_Launcher, "ensure_ghostscript")
    mocker.patch.object(AutoML_Launcher.memory_manager, "cleanup")
    spy = mocker.patch.object(runpy, "run_path")
    AutoML_Launcher.main()
    expected = Path(AutoML_Launcher.__file__).parent / "main" / "AutoML.py"
    spy.assert_called_once_with(expected, run_name="__main__")
