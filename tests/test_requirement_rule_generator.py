import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analysis.governance as governance
from analysis.requirement_rule_generator import generate_patterns_from_config


def test_generate_patterns_from_config(tmp_path: Path) -> None:
    cfg = {
        "requirement_rules": {
            "annotation": {"action": "annotate", "subject": "Team"}
        },
        "safety_ai_relation_rules": {"Annotation": {"ANN": ["Database"]}},
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    expected = {
        "SA-annotation-ANN-Database",
        "SA-annotation-ANN-Database-COND",
        "SA-annotation-ANN-Database-CONST",
        "SA-annotation-ANN-Database-COND-CONST",
    }
    assert ids == expected


def test_reload_config_updates_patterns(tmp_path: Path, monkeypatch) -> None:
    cfg = {
        "requirement_rules": {
            "augmentation": {"action": "augment", "subject": "Team"}
        },
        "safety_ai_relation_rules": {"Augmentation": {"ANN": ["Database"]}},
    }
    path = tmp_path / "diagram_rules.json"
    path.write_text(json.dumps(cfg))
    monkeypatch.setattr(governance, "_CONFIG_PATH", path)
    governance.reload_config()
    ids = {p["Pattern ID"] for p in governance._PATTERN_DEFS}
    assert "SA-augmentation-ANN-Database" in ids


def test_field_data_collection_uses_from() -> None:
    cfg = {
        "requirement_rules": {
            "field data collection": {
                "action": "collect field data",
                "subject": "Engineering team",
            }
        },
        "safety_ai_relation_rules": {
            "Field data collection": {"Database": ["Data acquisition"]}
        },
    }
    patterns = generate_patterns_from_config(cfg)
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"] == "SA-field_data_collection-Database-Data_acquisition"
    )
    assert "collect field data from the <target_id>" in tmpl


def test_rule_with_multiple_targets() -> None:
    cfg = {
        "requirement_rules": {
            "multi": {"action": "relate", "subject": "Team", "targets": 2}
        },
        "safety_ai_relation_rules": {"Multi": {"A": ["B"]}},
    }
    patterns = generate_patterns_from_config(cfg)
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"] == "SA-multi-A-B"
    )
    assert "<target2_id>" in tmpl
