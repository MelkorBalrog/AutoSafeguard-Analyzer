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
    assert expected.issubset(ids)


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


def test_governance_element_patterns() -> None:
    cfg = {
        "requirement_rules": {"approves": {"action": "approve", "subject": "Role"}},
        "governance_element_nodes": ["Role", "Document"],
        "governance_element_relations": ["Approves"],
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    expected = {
        "GOV-approves-Role-Document",
        "GOV-approves-Role-Document-COND",
        "GOV-approves-Role-Document-CONST",
        "GOV-approves-Role-Document-COND-CONST",
    }
    assert expected.issubset(ids)