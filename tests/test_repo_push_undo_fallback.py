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

import pytest
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def test_push_undo_state_falls_back_when_strategy_missing():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    base_len = len(repo._undo_stack)

    original = SysMLRepository._push_undo_state_v4
    del SysMLRepository._push_undo_state_v4
    try:
        repo.push_undo_state("v4")
        assert len(repo._undo_stack) == base_len + 1
    finally:
        SysMLRepository._push_undo_state_v4 = original
