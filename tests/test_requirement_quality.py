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

from analysis.requirement_quality import check_requirement_quality


def test_detects_bad_verb_form():
    text = "Safety engineer shall assesses the <object1_id> (<object1_class>)."
    passed, issues = check_requirement_quality(text)
    assert not passed
    assert any("base form" in msg for msg in issues)


def test_detects_missing_connectors():
    text = (
        "Safety engineer shall assess the <object1_id> (<object1_class>) using the "
        "<object0_id> (<object0_class>), mitigates the <object2_id> (<object2_class>), "
        "develops the <object3_id> (<object3_class>), verify the <object4_id> (<object4_class>), "
        "and produces the <object5_id> (<object5_class>) constrained by <constraint>."
    )
    passed, issues = check_requirement_quality(text)
    assert not passed
    assert any("connecting word" in msg for msg in issues)


def test_accepts_well_formed_requirement():
    text = (
        "Safety engineer shall assess the <object1_id> (<object1_class>) using the "
        "<object0_id> (<object0_class>), ensuring it mitigates the <object2_id> (<object2_class>), "
        "that develops the <object3_id> (<object3_class>), that verifies the <object4_id> (<object4_class>), "
        "and produces the <object5_id> (<object5_class>) constrained by <constraint>."
    )
    passed, issues = check_requirement_quality(text)
    assert passed, issues
