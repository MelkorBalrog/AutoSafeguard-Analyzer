#!/usr/bin/env python3
"""Wrapper launcher for AutoML.

This script ensures required third-party packages are available before
executing :mod:`AutoML`.  When run inside the PyInstaller-built
executable the dependencies are already bundled so the installation step
is skipped.
"""
import importlib
import runpy
import os
import subprocess
import sys
from pathlib import Path
from tools.crash_report_logger import install_best
from tools.memory_manager import manager as memory_manager

# Hint PyInstaller to bundle AutoML and its dependencies (e.g. gui package)
if False:  # pragma: no cover
    import AutoML  # noqa: F401
    Path(r"C:\\Program Files\\gs\\gs10.04.0\\bin\\gswin64c.exe")

REQUIRED_PACKAGES = {
    "pillow": "PIL",
    "openpyxl": "openpyxl",
    "networkx": "networkx",
    "matplotlib": "matplotlib",
    "reportlab": "reportlab",
    "adjustText": "adjustText",
}

GS_PATH = Path(r"C:\\Program Files\\gs\\gs10.04.0\\bin\\gswin64c.exe")


def _install_ghostscript_via_winget() -> bool:
    """Attempt installation using winget."""
    try:
        subprocess.check_call([
            "winget",
            "install",
            "--id",
            "Ghostscript.Ghostscript",
            "-e",
            "--silent",
        ])
        return True
    except Exception:
        return False


def _install_ghostscript_via_choco() -> bool:
    """Attempt installation using Chocolatey."""
    try:
        subprocess.check_call(["choco", "install", "ghostscript", "-y"])
        return True
    except Exception:
        return False


def _install_ghostscript_via_powershell() -> bool:
    """Download and install Ghostscript via PowerShell."""
    url = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10040/gs10040w64.exe"
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
    """Fallback installation using pip ghostscript wrapper."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ghostscript"])
        return True
    except Exception:
        return False


def ensure_ghostscript() -> None:
    """Ensure Ghostscript is available on Windows systems.

    The function attempts four different installation mechanisms to provide
    robustness across environments.  If all methods fail, a ``RuntimeError``
    is raised to signal the missing dependency.
    """
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
    """Install any missing runtime dependencies.

    When running from a PyInstaller executable, the packages are already
    bundled and pip is not available, so the function simply returns.
    """
    if getattr(sys, "frozen", False):
        return
    for pkg, module in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module)
        except ImportError:
            proc = subprocess.Popen([sys.executable, "-m", "pip", "install", pkg])
            memory_manager.register_process(pkg, proc)
            proc.wait()
    memory_manager.cleanup()

def main() -> None:
    """Entry point used by both source and bundled executions."""
    install_best()
    ensure_packages()
    ensure_ghostscript()
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    main_script = base_path / "main" / "AutoML.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(base_path), env.get("PYTHONPATH", "")]
    )
    subprocess.run(
        [sys.executable, str(main_script)],
        check=True,
        cwd=base_path,
        env=env,
    )
    memory_manager.cleanup()

if __name__ == "__main__":
    main()
