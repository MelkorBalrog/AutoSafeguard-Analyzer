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
    conns.setdefault("Reviews", {}).setdefault("Document", ["Record"])
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
