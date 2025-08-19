#!/usr/bin/env python3
"""Wrapper launcher for AutoML.

This script ensures required third-party packages are available before
executing :mod:`AutoML`.  When run inside the PyInstaller-built
executable the dependencies are already bundled so the installation step
is skipped.
"""
import importlib
import runpy
import subprocess
import sys
from pathlib import Path

REQUIRED_PACKAGES = [
    "pillow",
    "openpyxl",
    "networkx",
    "matplotlib",
    "reportlab",
    "adjustText",
]

def ensure_packages() -> None:
    """Install any missing runtime dependencies.

    When running from a PyInstaller executable, the packages are already
    bundled and pip is not available, so the function simply returns.
    """
    if getattr(sys, "frozen", False):
        return
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def main() -> None:
    ensure_packages()
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    script = base_path / "AutoML.py"
    runpy.run_path(str(script), run_name="__main__")

if __name__ == "__main__":
    main()
