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
from config import load_diagram_rules, validate_diagram_rules


def test_load_diagram_rules_rejects_invalid_connection_rules(tmp_path: Path) -> None:
    # Source mapping is not a list, should raise ValueError
    bad = {"connection_rules": {"Diag": {"Conn": {"Src": "Dst"}}}}
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        load_diagram_rules(path)


def test_validate_diagram_rules_accepts_valid_structure(tmp_path: Path) -> None:
    good = {"connection_rules": {"Diag": {"Conn": {"Src": ["Dst"]}}}}
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(good))
    data = load_diagram_rules(path)
    assert data["connection_rules"]["Diag"]["Conn"]["Src"] == ["Dst"]


def test_validate_diagram_rules_flags_invalid_list() -> None:
    with pytest.raises(ValueError):
        validate_diagram_rules({"ai_nodes": "not a list"})
