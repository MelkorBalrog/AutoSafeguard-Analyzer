#!/usr/bin/env python3
"""Wrapper launcher for AutoML.

This script ensures required third-party packages are available before
executing :mod:`AutoML`.  When run inside the PyInstaller-built
executable the dependencies are already bundled so the installation step
is skipped.
"""
import importlib
import os
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
    sys.path.insert(0, str(base_path))
    os.chdir(base_path)
    from AutoML import main as AutoML_main
    AutoML_main()

if __name__ == "__main__":
    main()
