"""Regression tests ensuring version consistency."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mainappsrc.version import VERSION


def _readme_version() -> str:
    """Extract the version string from the README."""

    first_line = ROOT.joinpath("README.md").read_text(encoding="utf-8").splitlines()[0]
    prefix, version = first_line.split(":", maxsplit=1)
    return version.strip()


def test_readme_matches_version() -> None:
    """README version must match the source version."""

    assert _readme_version() == VERSION


def test_cli_reports_same_version() -> None:
    """The ``--version`` flag should report the package version."""

    result = subprocess.run(
        [sys.executable, str(ROOT / "AutoML.py"), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == VERSION


