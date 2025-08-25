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

from __future__ import annotations

"""Unit tests for the TrashEater resource monitor."""

import sys
from pathlib import Path

# Ensure repository root is on sys.path for local imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.trash_eater import TrashEater


class DummyManager:
    """Minimal stand-in for the real memory manager."""

    def __init__(self) -> None:
        self.called = False

    def cleanup(self) -> None:  # pragma: no cover - simple flag setter
        self.called = True


def test_cleanup_triggered_when_above_threshold() -> None:
    """TrashEater should call cleanup when usage exceeds threshold."""

    mgr = DummyManager()
    eater = TrashEater(threshold=0.5, usage_provider=lambda: 0.6, manager=mgr)
    eater.check_once()
    assert mgr.called


def test_no_cleanup_below_threshold() -> None:
    """TrashEater should not clean when usage is below threshold."""

    mgr = DummyManager()
    eater = TrashEater(threshold=0.5, usage_provider=lambda: 0.4, manager=mgr)
    eater.check_once()
    assert not mgr.called
