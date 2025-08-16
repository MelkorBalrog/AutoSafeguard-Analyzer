import json
import types
from pathlib import Path

from gui import architecture


def test_governance_task_rule_allows_action(tmp_path, monkeypatch):
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
    win = architecture.GovernanceDiagramWindow.__new__(architecture.GovernanceDiagramWindow)
    win.repo = types.SimpleNamespace(diagrams={})
    win.diagram_id = "d"
    win.repo.diagrams["d"] = types.SimpleNamespace(diag_type="Governance Diagram")
    src = architecture.SysMLObject(1, "Action", 0, 0)
    dst = architecture.SysMLObject(2, "Work Product", 0, 0)
    valid, _ = architecture.GovernanceDiagramWindow.validate_connection(win, src, dst, "Produces")
    assert valid
    monkeypatch.setattr(architecture, "_CONFIG_PATH", orig_path)
    architecture.reload_config()
