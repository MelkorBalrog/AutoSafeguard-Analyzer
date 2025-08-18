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


def test_rule_with_custom_template_and_variables() -> None:
    cfg = {
        "requirement_rules": {
            "custom": {
                "action": "combine",
                "template": "<role> shall use <tool> with <condition>",
                "variables": ["<role>", "<tool>"],
            }
        },
        "safety_ai_relation_rules": {"Custom": {"R": ["T"]}},
    }
    patterns = generate_patterns_from_config(cfg)
    base = next(
        p for p in patterns if p["Pattern ID"] == "SA-custom-R-T"
    )
    assert base["Template"].startswith("<role> shall use <tool>")
    assert "<role>" in base["Variables"]
    assert "<tool>" in base["Variables"]


def test_sequence_rule_generation() -> None:
    cfg = {
        "safety_ai_relation_rules": {
            "Rel1": {"A": ["B"]},
            "Rel2": {"B": ["C"]},
        },
        "requirement_sequences": {
            "chain": {
                "relations": ["Rel1", "Rel2"],
                "subject": "Team",
                "action": "chain",
            }
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    assert "SEQ-chain-A-C" in ids
    tmpl = next(p["Template"] for p in patterns if p["Pattern ID"] == "SEQ-chain-A-C")
    assert "<target2_id>" in tmpl


def test_complex_sequences() -> None:
    cfg = {
        "safety_ai_relation_rules": {
            "Triage": {"Safety Issue": ["Field Data"]},
            "Develops": {"Field Data": ["Test Suite"]},
            "Constrains": {"Policy": ["Process"]},
            "Produces": {"Process": ["Document"], "Test Suite": ["Document"]},
            "Validate": {"Model": ["Test Suite"]},
        },
        "requirement_sequences": {
            "incident triage": {
                "relations": ["Triage", "Develops"],
                "subject": "Safety manager",
                "action": "trigger test development",
            },
            "policy compliance": {
                "relations": ["Constrains", "Produces"],
                "subject": "Governance team",
                "action": "enforce policy",
            },
            "model validation": {
                "relations": ["Validate", "Produces"],
                "subject": "Validation team",
                "action": "validate models",
            },
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    assert "SEQ-incident_triage-Safety_Issue-Test_Suite" in ids
    assert "SEQ-policy_compliance-Policy-Document" in ids
    assert "SEQ-model_validation-Model-Document" in ids
