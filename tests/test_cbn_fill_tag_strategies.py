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

import types

from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


def test_fill_tag_strategies_unique_and_ordered():
    win = object.__new__(CausalBayesianNetworkWindow)
    win.canvas = types.SimpleNamespace()
    tags = [
        win._fill_tag_strategy1("A", 0),
        win._fill_tag_strategy2("A", 0),
        win._fill_tag_strategy3("A", 0),
        win._fill_tag_strategy4("A", 0),
    ]
    assert len(set(tags)) == 4
    assert win._generate_fill_tag("A", 0) == tags[0]
