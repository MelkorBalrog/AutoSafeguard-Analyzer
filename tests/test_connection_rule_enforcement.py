import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui import architecture
from sysml.sysml_repository import SysMLRepository, SysMLRelationship


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
