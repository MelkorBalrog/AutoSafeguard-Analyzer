#!/usr/bin/env python3
# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Compatibility wrapper for the AutoML launcher.

This module proxies calls to :mod:`AutoML` so test suites and scripts can
simply ``import automl`` regardless of case sensitivity.
"""

import os
import subprocess
import importlib
import sys
from concurrent.futures import ThreadPoolExecutor

from pathlib import Path
from tools.memory_manager import manager as memory_manager

import AutoML as _launcher
from AutoML import *  # noqa: F401,F403 - re-export documented API

GS_PATH = Path(r"C:\\Program Files\\gs\\gs10.04.0\\bin\\gswin64c.exe")
REQUIRED_PACKAGES = [
    "pillow",
    "openpyxl",
    "networkx",
    "matplotlib",
    "reportlab",
    "adjustText",
]


def _install_ghostscript_via_winget() -> bool:
    try:
        subprocess.check_call(["winget"])
        return True
    except Exception:
        return False


def _install_ghostscript_via_choco() -> bool:
    try:
        subprocess.check_call(["choco"])
        return True
    except Exception:
        return False


def _install_ghostscript_via_powershell() -> bool:
    try:
        subprocess.check_call(["powershell"])
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
    """Ensure Ghostscript is available on Windows systems."""
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
    if getattr(sys, "frozen", False):
        return
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if not missing:
        return
    def install(pkg: str) -> None:
        proc = subprocess.Popen([sys.executable, "-m", "pip", "install", pkg])
        memory_manager.register_process(pkg, proc)
        proc.wait()
    with ThreadPoolExecutor() as executor:
        executor.map(install, missing)
    memory_manager.cleanup()
