import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import load_diagram_rules, validate_diagram_rules


def test_load_diagram_rules_rejects_invalid_connection_rules(tmp_path: Path) -> None:
    # Source mapping is not a list, should raise ValueError
    bad = {"connection_rules": {"Diag": {"Conn": {"Src": "Dst"}}}}
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        load_diagram_rules(path)


def test_validate_diagram_rules_accepts_valid_structure(tmp_path: Path) -> None:
    good = {"connection_rules": {"Diag": {"Conn": {"Src": ["Dst"]}}}}
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(good))
    data = load_diagram_rules(path)
    assert data["connection_rules"]["Diag"]["Conn"]["Src"] == ["Dst"]


def test_validate_diagram_rules_flags_invalid_list() -> None:
    with pytest.raises(ValueError):
        validate_diagram_rules({"ai_nodes": "not a list"})
