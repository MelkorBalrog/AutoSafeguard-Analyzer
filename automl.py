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

"""Lightweight wrapper exposing launcher utilities for tests.

The test suite expects an :mod:`automl` module providing functions like
``ensure_packages`` and ``ensure_ghostscript``.  The main launcher lives in
``AutoML.py`` with a capitalised name, so this module simply re-exports all of
its public objects for convenience and to ease test imports.
"""

from AutoML import *  # noqa: F401,F403

