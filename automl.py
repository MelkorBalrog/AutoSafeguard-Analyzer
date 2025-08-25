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
"""Compatibility wrapper for the AutoML launcher."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

spec = spec_from_file_location("AutoMLLauncher", Path(__file__).with_name("AutoML.py"))
_launcher = module_from_spec(spec)
spec.loader.exec_module(_launcher)  # type: ignore[assignment]

REQUIRED_PACKAGES = _launcher.REQUIRED_PACKAGES
ensure_packages = _launcher.ensure_packages
ensure_ghostscript = _launcher.ensure_ghostscript
importlib = _launcher.importlib
subprocess = _launcher.subprocess
memory_manager = _launcher.memory_manager
os = _launcher.os
GS_PATH = _launcher.GS_PATH

__all__ = [
    "REQUIRED_PACKAGES",
    "ensure_packages",
    "ensure_ghostscript",
    "importlib",
    "subprocess",
    "memory_manager",
    "os",
    "GS_PATH",
]
