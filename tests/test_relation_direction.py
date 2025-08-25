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

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import load_diagram_rules

def _safety_ai_rules():
    cfg_path = (
        Path(__file__).resolve().parents[1]
        / "config"
        / "rules"
        / "diagram_rules.json"
    )
    cfg = load_diagram_rules(cfg_path)
    return cfg.get('connection_rules', {}).get('Governance Diagram', {})

def test_data_acquisition_relation_direction():
    rules = _safety_ai_rules()
    acq = rules.get("Acquisition", {})
    assert acq.get("AI Database") == ["Data acquisition"]
    fr_eval = rules.get("Field risk evaluation", {})
    assert fr_eval.get("AI Database") == ["Data acquisition"]
    fd_collect = rules.get("Field data collection", {})
    assert fd_collect.get("AI Database") == ["Data acquisition", "Task"]


def test_curation_process_data():
    rules = _safety_ai_rules()
    cur = rules.get("Curation", {})
    assert cur.get("Process") == ["Data"]
