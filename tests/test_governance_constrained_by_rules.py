import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import load_diagram_rules


def test_constrained_by_rules() -> None:
    cfg = load_diagram_rules(
        Path(__file__).resolve().parents[1]
        / "config"
        / "rules"
        / "diagram_rules.json"
    )
    rules = cfg["connection_rules"]["Governance Diagram"]["Constrained by"]
    assert set(rules["Organization"]) == {"Policy"}
    assert set(rules["Business Unit"]) == {"Principle"}
    assert set(rules["Work Product"]) == {
        "Guideline",
        "Policy",
        "Principle",
        "Standard",
        "Work Product",
    }
