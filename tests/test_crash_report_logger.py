import sys
from pathlib import Path

import pytest

# Ensure repository root is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.crash_report_logger import (
    crash_handler_v1,
    crash_handler_v2,
    CrashLoggerV3,
    CrashLoggerV4,
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
