import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui import architecture
from config import load_json_with_comments


def test_connection_rules_reload(tmp_path, monkeypatch):
    orig_path = architecture._CONFIG_PATH
    cfg = load_json_with_comments(orig_path)
    assert "Action" not in cfg["connection_rules"]["Governance Diagram"]["Produces"]
    new_cfg = json.loads(json.dumps(cfg))  # deep copy
    new_cfg["connection_rules"]["Governance Diagram"]["Produces"]["Action"] = ["Work Product"]
    tmp_file = tmp_path / "diagram_rules.json"
    tmp_file.write_text(json.dumps(new_cfg))
    try:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", tmp_file)
        architecture.reload_config()
        assert "Work Product" in architecture.CONNECTION_RULES["Governance Diagram"]["Produces"]["Action"]
    finally:
        monkeypatch.setattr(architecture, "_CONFIG_PATH", orig_path)
        architecture.reload_config()
