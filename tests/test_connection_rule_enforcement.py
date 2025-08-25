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
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui import architecture
from mainappsrc.models.sysml.sysml_repository import SysMLRepository, SysMLRelationship


def test_connection_rules_enforced_on_reload(tmp_path, monkeypatch):
    cfg = {
        "connection_rules": {
            "Governance Diagram": {"Produces": {"Task": ["Work Product"]}}
        }
    }
    path = tmp_path / "diagram_rules.json"
    path.write_text(json.dumps(cfg))
    orig_path = architecture._CONFIG_PATH
    monkeypatch.setattr(architecture, "_CONFIG_PATH", path)
    architecture.reload_config()

    repo = SysMLRepository.reset_instance()
    diag = repo.create_diagram("Governance Diagram")
    diag.objects = [
        {"obj_id": 1, "obj_type": "Task"},
        {"obj_id": 2, "obj_type": "Work Product"},
    ]
    rel = SysMLRelationship("r1", "Produces", "s", "t")
    repo.relationships.append(rel)
    diag.connections = [
        {"src": 1, "dst": 2, "conn_type": "Produces", "element_id": "r1"}
    ]
    diag.relationships = ["r1"]

    path.write_text(
        json.dumps({"connection_rules": {"Governance Diagram": {"Produces": {}}}})
    )
    architecture.reload_config()

    assert diag.connections == []
    assert repo.relationships == []

    monkeypatch.setattr(architecture, "_CONFIG_PATH", orig_path)
    architecture.reload_config()
