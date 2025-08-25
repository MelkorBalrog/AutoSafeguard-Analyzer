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

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import load_requirement_patterns, validate_requirement_patterns


def test_load_requirement_patterns_rejects_invalid_structure(tmp_path: Path) -> None:
    bad = [{"Pattern ID": "A", "Trigger": "t", "Template": "tmpl", "Variables": "x"}]
    path = tmp_path / "patterns.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        load_requirement_patterns(path)


def test_validate_requirement_patterns_accepts_valid_structure(tmp_path: Path) -> None:
    good = [{"Pattern ID": "A", "Trigger": "t", "Template": "tmpl", "Variables": ["<v>"]}]
    path = tmp_path / "patterns.json"
    path.write_text(json.dumps(good))
    data = load_requirement_patterns(path)
    assert data[0]["Pattern ID"] == "A"


def test_validate_requirement_patterns_requires_list() -> None:
    with pytest.raises(ValueError):
        validate_requirement_patterns({})
