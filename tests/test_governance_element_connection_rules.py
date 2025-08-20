import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import load_diagram_rules


def test_governance_element_connection_rules():
    cfg = load_diagram_rules(Path(__file__).resolve().parents[1] / "config/diagram_rules.json")
    rules = cfg["connection_rules"]["Governance Diagram"]
    assert set(rules["Approves"]["Role"]) == {"Document", "Policy", "Procedure", "Record"}
    assert set(rules["Uses"]["Role"]) == {"Document", "Data", "Record", "Work Product"}
    assert set(rules["Executes"]["Operation"]) == {
        "Procedure",
        "Process",
        "Work Product",
    }
    assert set(rules["Uses"]["Operation"]) == {"Data", "Document", "Record"}
    assert set(rules["Used By"]["Guideline"]) == {"Lifecycle Phase"}
    assert set(rules["Used By"]["Policy"]) == {"Lifecycle Phase"}
    assert set(rules["Used By"]["Principle"]) == {"Lifecycle Phase"}
    assert set(rules["Used By"]["Standard"]) == {"Lifecycle Phase"}
    assert set(rules["Constrained by"]["Organization"]) == {"Policy"}
    assert set(rules["Constrained by"]["Work Product"]) == {
        "Guideline",
        "Policy",
        "Principle",
        "Standard",
        "Work Product",
    }
