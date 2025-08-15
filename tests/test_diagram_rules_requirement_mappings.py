import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import load_diagram_rules


def test_all_connectors_have_requirement_rules():
    cfg = load_diagram_rules(Path(__file__).resolve().parents[1] / "config/diagram_rules.json")
    connectors = set()
    for conns in cfg.get("connection_rules", {}).values():
        for conn in conns:
            if conn.lower() == "flow":
                continue
            connectors.add(conn.lower())
    rules = set(cfg.get("requirement_rules", {}).keys())
    missing = connectors - rules
    assert not missing, f"Missing requirement rules for: {sorted(missing)}"
