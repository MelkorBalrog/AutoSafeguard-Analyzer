import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import load_requirement_patterns, validate_requirement_patterns


def test_load_requirement_patterns_rejects_invalid_structure(tmp_path: Path) -> None:
    bad = [{"Pattern ID": "A", "Trigger": "t", "Template": "tmpl", "Variables": "x"}]
    path = tmp_path / "patterns.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        load_requirement_patterns(path)


def test_validate_requirement_patterns_accepts_valid_structure(tmp_path: Path) -> None:
    good = [{"Pattern ID": "A", "Trigger": "t", "Template": "tmpl", "Variables": ["<v>"]}]
    path = tmp_path / "patterns.json"
    path.write_text(json.dumps(good))
    data = load_requirement_patterns(path)
    assert data[0]["Pattern ID"] == "A"


def test_validate_requirement_patterns_requires_list() -> None:
    with pytest.raises(ValueError):
        validate_requirement_patterns({})
