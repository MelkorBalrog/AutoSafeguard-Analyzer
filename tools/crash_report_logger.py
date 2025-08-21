"""Crash report logging utilities with multiple implementations."""

from __future__ import annotations

import datetime
import logging
import sys
import traceback
from pathlib import Path

# Default directory for crash logs
LOG_DIR = Path(__file__).resolve().parent


def crash_handler_v1(exc_type, exc, tb, path: Path | None = None) -> Path:
    """Write traceback to a fixed file using basic file IO."""
    log_path = path or LOG_DIR / "crash_v1.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as fh:
        traceback.print_exception(exc_type, exc, tb, file=fh)
    return log_path


def crash_handler_v2(exc_type, exc, tb, path: Path | None = None) -> Path:
    """Use :mod:`logging` to persist the crash details."""
    log_path = path or LOG_DIR / "crash_v2.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=log_path, level=logging.ERROR, force=True)
    logging.error("Unhandled exception", exc_info=(exc_type, exc, tb))
    return log_path


class CrashLoggerV3:
    """Callable class writing traceback to a provided path."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, exc_type, exc, tb) -> Path:
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("Unhandled exception\n")
            traceback.print_exception(exc_type, exc, tb, file=fh)
        return self.path


def crash_handler_v3(exc_type, exc, tb, path: Path | None = None) -> Path:
    """Helper using :class:`CrashLoggerV3` for a default path."""
    return CrashLoggerV3(path or LOG_DIR / "crash_v3.log")(exc_type, exc, tb)


class CrashLoggerV4:
    """Timestamped crash logger producing unique files."""

    def __init__(self, directory: Path | str = LOG_DIR):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def __call__(self, exc_type, exc, tb) -> Path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_path = self.directory / f"crash_{timestamp}.log"
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(f"Timestamp: {timestamp}\n")
            fh.write("Unhandled exception\n")
            traceback.print_exception(exc_type, exc, tb, file=fh)
        return log_path


def install_v1() -> None:
    sys.excepthook = crash_handler_v1


def install_v2() -> None:
    sys.excepthook = crash_handler_v2


def install_v3() -> None:
    sys.excepthook = crash_handler_v3


def install_v4(directory: Path | str = LOG_DIR) -> None:
    sys.excepthook = CrashLoggerV4(directory)


# The most complete implementation is version 4
install_best = install_v4

__all__ = [
    "crash_handler_v1",
    "crash_handler_v2",
    "CrashLoggerV3",
    "crash_handler_v3",
    "CrashLoggerV4",
    "install_v1",
    "install_v2",
    "install_v3",
    "install_v4",
    "install_best",
]
