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

from analysis.utils import (
    exposure_to_probability,
    controllability_to_probability,
    severity_to_probability,
    update_probability_tables,
    EXPOSURE_PROBABILITIES,
    CONTROLLABILITY_PROBABILITIES,
    SEVERITY_PROBABILITIES,
    normalize_probability_mapping,
)


def test_update_probability_tables():
    defaults = (
        EXPOSURE_PROBABILITIES.copy(),
        CONTROLLABILITY_PROBABILITIES.copy(),
        SEVERITY_PROBABILITIES.copy(),
    )
    update_probability_tables({1: 0.2}, {2: 0.3}, {3: 0.4})
    assert exposure_to_probability(1) == 0.2
    assert controllability_to_probability(2) == 0.3
    assert severity_to_probability(3) == 0.4
    # Restore defaults to avoid side effects
    update_probability_tables(*defaults)


def test_normalize_probability_mapping():
    data = {"1": "0.1", "2": 0.2}
    result = normalize_probability_mapping(data)
    assert result == {1: 0.1, 2: 0.2}
