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
from config import load_json_with_comments


def test_toolbox_updates_with_new_relation(tmp_path, monkeypatch):
    orig_path = architecture._CONFIG_PATH
    cfg = load_json_with_comments(orig_path)
    before = architecture._toolbox_defs()
    assert "Reviews" not in before["Artifacts"]["relations"]
    new_cfg = json.loads(json.dumps(cfg))
    conns = new_cfg["connection_rules"].setdefault("Governance Diagram", {})
    # Add a new relation between two artifact types to ensure it surfaces only
    # in the Artifacts toolbox.
    conns.setdefault("Reviews", {})["Document"] = ["Record"]
    tmp_file = tmp_path / "diagram_rules.json"
    tmp_file.write_text(json.dumps(new_cfg))
    try:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", tmp_file)
        architecture.reload_config()
        after = architecture._toolbox_defs()
        assert "Reviews" in after["Artifacts"]["relations"]
        assert "Reviews" not in after.get("Entities", {}).get("relations", [])
    finally:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", orig_path)
        architecture.reload_config()


def test_irrelevant_relations_filtered():
    defs = architecture._toolbox_defs()
    # "Propagate" appears in the configuration for Business Unit with no
    # allowed targets.  It should therefore be excluded from the Entities
    # toolbox relations.
    assert "Propagate" not in defs["Entities"]["relations"]
    # "Approves" connects Roles to Documents/Records but cannot originate from
    # an artifact, so it should not appear in either toolbox.
    assert "Approves" not in defs["Artifacts"]["relations"]
    assert "Approves" not in defs["Entities"]["relations"]


def test_cross_category_relations_surface():
    defs = architecture._toolbox_defs()
    art_ext = defs["Artifacts"]["externals"]
    assert "Entities" in art_ext
    assert "Role" in art_ext["Entities"]["nodes"]
    assert "Approves" in art_ext["Entities"]["relations"]


def test_governance_core_relations_and_externals(tmp_path, monkeypatch):
    defs = architecture._toolbox_defs()
    core = defs["Governance Core"]
    # Governance core toolbox hides Work Product and Lifecycle Phase buttons
    # but should still expose all relationships between them.
    assert core["nodes"] == []
    relations = core["relations"]
    assert {
        "Propagate",
        "Propagate by Review",
        "Propagate by Approval",
        "Re-use",
        "Used By",
    } <= set(relations)
    assert relations.index("Used By") < relations.index("Used after Approval")
    orig_path = architecture._CONFIG_PATH
    cfg = load_json_with_comments(orig_path)
    new_cfg = json.loads(json.dumps(cfg))
    conns = new_cfg["connection_rules"].setdefault("Governance Diagram", {})
    conns.setdefault("Reviews", {})["Work Product"] = ["Document"]
    tmp_file = tmp_path / "diagram_rules.json"
    tmp_file.write_text(json.dumps(new_cfg))
    try:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", tmp_file)
        architecture.reload_config()
        updated = architecture._toolbox_defs()
        ext = updated["Governance Core"]["externals"]["Artifacts"]
        assert "Document" in ext["nodes"]
        assert "Reviews" in ext["relations"]
    finally:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", orig_path)
        architecture.reload_config()


def test_bidirectional_external_relations(tmp_path, monkeypatch):
    orig_path = architecture._CONFIG_PATH
    cfg = load_json_with_comments(orig_path)
    new_cfg = json.loads(json.dumps(cfg))
    conns = new_cfg["connection_rules"].setdefault("Governance Diagram", {})
    # Introduce a relation from an artifact to an entity so both toolboxes
    # expose it under their related sections.
    conns.setdefault("Creates", {}).setdefault("Document", ["Role"])
    tmp_file = tmp_path / "diagram_rules.json"
    tmp_file.write_text(json.dumps(new_cfg))
    try:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", tmp_file)
        architecture.reload_config()
        defs = architecture._toolbox_defs()
        art_ext = defs["Artifacts"]["externals"]["Entities"]
        assert "Role" in art_ext["nodes"]
        assert "Creates" in art_ext["relations"]
        ent_ext = defs["Entities"]["externals"]["Artifacts"]
        assert "Document" in ent_ext["nodes"]
        assert "Creates" in ent_ext["relations"]
    finally:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", orig_path)
        architecture.reload_config()
