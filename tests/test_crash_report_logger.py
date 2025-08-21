import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# Ensure repository root is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.crash_report_logger import (
    CrashLoggerV3,
    CrashLoggerV4,
    crash_handler_v1,
    crash_handler_v2,
    watchdog_v1,
    watchdog_v2,
    watchdog_v3,
    watchdog_v4,
)


def _raise(exception):
    try:
        raise exception
    except Exception:
        return sys.exc_info()


def test_crash_handler_v1(tmp_path):
    path = tmp_path / "v1.log"
    exc_info = _raise(ValueError("boom"))
    crash_handler_v1(*exc_info, path=path)
    assert path.exists()
    assert "ValueError: boom" in path.read_text()


def test_crash_handler_v2(tmp_path):
    path = tmp_path / "v2.log"
    exc_info = _raise(RuntimeError("oops"))
    crash_handler_v2(*exc_info, path=path)
    assert path.exists()
    assert "RuntimeError: oops" in path.read_text()


def test_crash_handler_v3(tmp_path):
    path = tmp_path / "v3.log"
    handler = CrashLoggerV3(path)
    handler(*_raise(KeyError("missing")))
    assert path.exists()
    assert "KeyError: 'missing'" in path.read_text()


def test_crash_handler_v4(tmp_path):
    directory = tmp_path / "logs"
    handler = CrashLoggerV4(directory)
    handler(*_raise(Exception("crash")))
    files = list(directory.glob("crash_*.log"))
    assert files, "log file not created"
    assert "Exception: crash" in files[0].read_text()


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_subprocess(code: str, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    base_env = os.environ.copy()
    base_env.update(env or {})
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        timeout=5,
        env=base_env,
    )


def test_watchdog_v1(tmp_path):
    log = tmp_path / "wd1.log"
    code = f"""
    from tools.crash_report_logger import watchdog_v1
    watchdog_v1(timeout=0.5, path=r"{log.as_posix()}")
    import time
    time.sleep(10)
    """
    proc = _run_subprocess(code, env={"PYTHONPATH": str(REPO_ROOT)})
    assert proc.returncode == 1
    assert log.exists()
    assert "TimeoutError: Watchdog timeout" in log.read_text()


def test_watchdog_v2(tmp_path):
    log = tmp_path / "wd2.log"
    code = f"""
    from tools.crash_report_logger import watchdog_v2
    watchdog_v2(timeout=0.5, path=r"{log.as_posix()}")
    import time
    time.sleep(10)
    """
    proc = _run_subprocess(code, env={"PYTHONPATH": str(REPO_ROOT)})
    assert proc.returncode == 1
    assert log.exists()
    assert "TimeoutError: Watchdog timeout" in log.read_text()


def test_watchdog_v3(tmp_path):
    log = tmp_path / "wd3.log"
    code = f"""
    from tools.crash_report_logger import watchdog_v3
    watchdog_v3(timeout=0.5, path=r"{log.as_posix()}")
    import time
    time.sleep(10)
    """
    proc = _run_subprocess(code, env={"PYTHONPATH": str(REPO_ROOT)})
    assert proc.returncode == 1
    assert log.exists()
    assert "TimeoutError: Watchdog timeout" in log.read_text()


def test_watchdog_v4(tmp_path):
    directory = tmp_path / "logs"
    code = f"""
    from tools.crash_report_logger import watchdog_v4
    watchdog_v4(timeout=0.5, directory=r"{directory.as_posix()}")
    import time
    time.sleep(10)
    """
    proc = _run_subprocess(code, env={"PYTHONPATH": str(REPO_ROOT)})
    assert proc.returncode == 1
    files = list(directory.glob("crash_*.log"))
    assert files
    assert "TimeoutError: Watchdog timeout" in files[0].read_text()
