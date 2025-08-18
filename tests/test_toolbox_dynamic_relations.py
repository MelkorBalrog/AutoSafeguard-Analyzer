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
    assert "Reviews" not in before["Entities"]["relations"]
    assert "Reviews" not in before["Artifacts"]["relations"]
    new_cfg = json.loads(json.dumps(cfg))
    conns = new_cfg["connection_rules"].setdefault("Governance Diagram", {})
    conns.setdefault("Reviews", {})["Role"] = ["Document"]
    tmp_file = tmp_path / "diagram_rules.json"
    tmp_file.write_text(json.dumps(new_cfg))
    try:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", tmp_file)
        architecture.reload_config()
        after = architecture._toolbox_defs()
        assert "Reviews" in after["Entities"]["relations"]
        assert "Reviews" in after["Artifacts"]["relations"]
    finally:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", orig_path)
        architecture.reload_config()


def test_irrelevant_relations_filtered():
    defs = architecture._toolbox_defs()
    # "Propagate" appears in the configuration for Business Unit with no
    # allowed targets.  It should therefore be excluded from the Entities
    # toolbox relations.
    assert "Propagate" not in defs["Entities"]["relations"]
