"""Lightweight launcher utilities for AutoML used in tests."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tools.memory_manager import manager as memory_manager

REQUIRED_PACKAGES = [
    "pillow",
    "openpyxl",
    "networkx",
    "matplotlib",
    "reportlab",
    "adjustText",
]

GS_PATH = Path(r"C:\\Program Files\\gs\\gs10.04.0\\bin\\gswin64c.exe")


def _install_ghostscript_via_winget() -> bool:
    try:
        subprocess.check_call(
            ["winget", "install", "--id", "Ghostscript.Ghostscript", "-e", "--silent"]
        )
        return True
    except Exception:
        return False


def _install_ghostscript_via_choco() -> bool:
    try:
        subprocess.check_call(["choco", "install", "ghostscript", "-y"])
        return True
    except Exception:
        return False


def _install_ghostscript_via_powershell() -> bool:
    url = (
        "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10040/gs10040w64.exe"
    )
    script = (
        f"Invoke-WebRequest -Uri {url} -OutFile gs.exe;"
        "Start-Process gs.exe -ArgumentList '/S' -NoNewWindow -Wait"
    )
    try:
        subprocess.check_call(["powershell", "-Command", script])
        return True
    except Exception:
        return False


def _install_ghostscript_via_pip() -> bool:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ghostscript"])
        return True
    except Exception:
        return False


def ensure_ghostscript() -> None:
    """Ensure Ghostscript is installed on Windows systems."""
    if os.name != "nt":
        return
    if GS_PATH.exists():
        return
    installers = [
        _install_ghostscript_via_winget,
        _install_ghostscript_via_choco,
        _install_ghostscript_via_powershell,
        _install_ghostscript_via_pip,
    ]
    for installer in installers:
        if installer():
            if GS_PATH.exists():
                return
    raise RuntimeError("Ghostscript installation failed")


def ensure_packages() -> None:
    """Install any missing runtime dependencies."""
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except Exception:
            missing.append(pkg)
    if not missing:
        return

    def install(name: str) -> None:
        subprocess.Popen([sys.executable, "-m", "pip", "install", name])

    with ThreadPoolExecutor() as executor:
        executor.map(install, missing)
    memory_manager.cleanup()


__all__ = [
    "ensure_ghostscript",
    "ensure_packages",
    "REQUIRED_PACKAGES",
    "GS_PATH",
    "os",
    "subprocess",
    "importlib",
    "memory_manager",
]
