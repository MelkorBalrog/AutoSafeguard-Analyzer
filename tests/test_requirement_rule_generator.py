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
        "ai_nodes": ["ANN", "AI Database"],
        "requirement_rules": {
            "annotation": {"action": "annotate", "subject": "Team"}
        },
        "connection_rules": {
            "Governance Diagram": {"Annotation": {"ANN": ["AI Database"]}}
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    expected = {
        "SA-annotation-ANN-AI_Database",
        "SA-annotation-ANN-AI_Database-COND",
        "SA-annotation-ANN-AI_Database-CONST",
        "SA-annotation-ANN-AI_Database-COND-CONST",
        "SA-annotation-ANN-AI_Database-ROLE",
        "SA-annotation-ANN-AI_Database-ROLE-COND",
        "SA-annotation-ANN-AI_Database-ROLE-CONST",
        "SA-annotation-ANN-AI_Database-ROLE-COND-CONST",
    }
    assert ids == expected


def test_reload_config_updates_patterns(tmp_path: Path, monkeypatch) -> None:
    cfg = {
        "ai_nodes": ["ANN", "AI Database"],
        "requirement_rules": {
            "augmentation": {"action": "augment", "subject": "Team"}
        },
        "connection_rules": {
            "Governance Diagram": {"Augmentation": {"ANN": ["AI Database"]}}
        },
    }
    path = tmp_path / "diagram_rules.json"
    path.write_text(json.dumps(cfg))
    monkeypatch.setattr(governance, "_CONFIG_PATH", path)
    governance.reload_config()
    ids = {p["Pattern ID"] for p in governance._PATTERN_DEFS}
    assert "SA-augmentation-ANN-AI_Database" in ids


def test_field_data_collection_uses_from() -> None:
    cfg = {
        "ai_nodes": ["AI Database", "Data acquisition"],
        "requirement_rules": {
            "field data collection": {
                "action": "collect field data",
                "subject": "Engineering team",
            }
        },
        "connection_rules": {
            "Governance Diagram": {
                "Field data collection": {"AI Database": ["Data acquisition"]}
            }
        },
    }
    patterns = generate_patterns_from_config(cfg)
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"] == "SA-field_data_collection-AI_Database-Data_acquisition"
    )
    assert "collect field data from the <object1_id>" in tmpl


def test_rule_with_multiple_targets() -> None:
    cfg = {
        "ai_nodes": ["A", "B"],
        "requirement_rules": {
            "multi": {"action": "relate", "subject": "Team", "targets": 2}
        },
        "connection_rules": {"Governance Diagram": {"Multi": {"A": ["B"]}}},
    }
    patterns = generate_patterns_from_config(cfg)
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"] == "SA-multi-A-B"
    )
    assert "<object2_id>" in tmpl


def test_rule_with_custom_template_and_variables() -> None:
    cfg = {
        "ai_nodes": ["R", "T"],
        "requirement_rules": {
            "custom": {
                "action": "combine",
                "template": "<role> shall use <tool> with <condition>",
                "variables": ["<role>", "<tool>"],
            }
        },
        "connection_rules": {"Governance Diagram": {"Custom": {"R": ["T"]}}},
    }
    patterns = generate_patterns_from_config(cfg)
    base = next(
        p for p in patterns if p["Pattern ID"] == "SA-custom-R-T"
    )
    assert base["Template"].startswith("<role> shall use <tool>")
    assert "<role>" in base["Variables"]
    assert "<tool>" in base["Variables"]


def test_rule_role_subject_variant() -> None:
    cfg = {
        "ai_nodes": ["ANN", "AI Database"],
        "requirement_rules": {
            "annotation": {"action": "annotate", "subject": "Team"}
        },
        "connection_rules": {
            "Governance Diagram": {"Annotation": {"ANN": ["AI Database"]}}
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    assert "SA-annotation-ANN-AI_Database" in ids
    assert "SA-annotation-ANN-AI_Database-ROLE" in ids
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"] == "SA-annotation-ANN-AI_Database-ROLE"
    )
    assert tmpl.startswith("<subject_id> (<subject_class>) shall annotate")
    assert "using the <object0_id>" not in tmpl


def test_sequence_rule_generation() -> None:
    cfg = {
        "ai_nodes": ["A", "B", "C"],
        "connection_rules": {
            "Governance Diagram": {
                "Rel1": {"A": ["B"]},
                "Rel2": {"B": ["C"]},
            }
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
    assert "<object2_id>" in tmpl
    assert "rel1" in tmpl and "rel2" in tmpl


def test_sequence_role_subject_variants() -> None:
    cfg = {
        "connection_rules": {
            "Governance Diagram": {
                "Responsible for": {"Role": ["Process"]},
                "Produces": {"Process": ["Document"]},
            }
        },
        "requirement_sequences": {
            "accountability": {
                "relations": ["Responsible for", "Produces"],
                "subject": "Governance board",
            }
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    assert "SEQ-accountability-Role-Document" in ids
    assert "SEQ-accountability_role_subject-Role-Document" in ids
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"] == "SEQ-accountability_role_subject-Role-Document"
    )
    assert tmpl.startswith("<subject_id> (<subject_class>) shall responsible for")
    assert "using the <object0_id>" not in tmpl


def test_sequence_organization_subject_variants() -> None:
    cfg = {
        "connection_rules": {
            "Governance Diagram": {
                "Leads": {"Organization": ["Process"]},
                "Produces": {"Process": ["Document"]},
            }
        },
        "requirement_sequences": {
            "management": {
                "relations": ["Leads", "Produces"],
                "subject": "Management team",
            }
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    assert "SEQ-management-Organization-Document" in ids
    assert "SEQ-management_organization_subject-Organization-Document" in ids
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"] == "SEQ-management_organization_subject-Organization-Document"
    )
    assert tmpl.startswith("<subject_id> (<subject_class>) shall leads")
    assert "using the <object0_id>" not in tmpl


def test_sequence_business_unit_subject_variants() -> None:
    cfg = {
        "connection_rules": {
            "Governance Diagram": {
                "Owns": {"Business Unit": ["Process"]},
                "Produces": {"Process": ["Document"]},
            }
        },
        "requirement_sequences": {
            "responsibility": {
                "relations": ["Owns", "Produces"],
                "subject": "Business leadership",
            }
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    assert "SEQ-responsibility-Business_Unit-Document" in ids
    assert (
        "SEQ-responsibility_business_unit_subject-Business_Unit-Document" in ids
    )
    tmpl = next(
        p["Template"]
        for p in patterns
        if p["Pattern ID"]
        == "SEQ-responsibility_business_unit_subject-Business_Unit-Document"
    )
    assert tmpl.startswith("<subject_id> (<subject_class>) shall owns")
    assert "using the <object0_id>" not in tmpl


def test_complex_sequences() -> None:
    cfg = {
        "ai_nodes": [
            "Safety Issue",
            "Field Data",
            "Test Suite",
            "Mitigation Plan",
            "Risk Assessment",
            "Policy",
            "Process",
            "Document",
            "Report",
            "Verification Plan",
            "Model",
            "Hazard",
            "Security Threat",
        ],
        "connection_rules": {
            "Governance Diagram": {
                "Triage": {"Safety Issue": ["Field Data"]},
                "Develops": {
                    "Field Data": ["Test Suite"],
                    "Mitigation Plan": ["Test Suite"],
                    "Risk Assessment": ["Test Suite"],
                },
                "Constrains": {"Policy": ["Process"]},
                "Produces": {
                    "Process": ["Document"],
                    "Test Suite": ["Document"],
                    "Report": ["Document"],
                    "Verification Plan": ["Document"],
                },
                "Validate": {
                    "Model": ["Test Suite"],
                    "Mitigation Plan": ["Report"],
                    "Test Suite": ["Report"],
                },
                "Assesses": {
                    "Hazard": ["Risk Assessment"],
                    "Security Threat": ["Risk Assessment"],
                    "Field Data": ["Risk Assessment"],
                },
                "Mitigates": {"Risk Assessment": ["Mitigation Plan"]},
                "Verify": {"Test Suite": ["Verification Plan"]},
            }
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
            "hazard mitigation": {
                "relations": ["Assesses", "Mitigates", "Develops", "Produces"],
                "subject": "Safety engineer",
                "action": "develop hazard mitigation tests",
            },
            "incident validation": {
                "relations": ["Triage", "Develops", "Validate", "Produces"],
                "subject": "Safety manager",
                "action": "validate incident resolution",
            },
            "hazard verification": {
                "relations": ["Assesses", "Mitigates", "Develops", "Verify", "Produces"],
                "subject": "Safety engineer",
                "action": "verify hazard mitigations",
            },
            "cybersecurity threat verification": {
                "relations": ["Assesses", "Mitigates", "Develops", "Verify", "Produces"],
                "subject": "Cybersecurity team",
                "action": "verify threat mitigations",
            },
            "sotif scenario verification": {
                "relations": ["Assesses", "Develops", "Verify", "Produces"],
                "subject": "Validation team",
                "action": "verify scenarios",
            },
        },
    }
    patterns = generate_patterns_from_config(cfg)
    ids = {p["Pattern ID"] for p in patterns}
    assert "SEQ-incident_triage-Safety_Issue-Test_Suite" in ids
    assert "SEQ-policy_compliance-Policy-Document" in ids
    assert "SEQ-model_validation-Model-Document" in ids
    assert "SEQ-hazard_mitigation-Hazard-Document" in ids
    assert "SEQ-incident_validation-Safety_Issue-Document" in ids
    assert "SEQ-hazard_verification-Hazard-Document" in ids
    assert "SEQ-cybersecurity_threat_verification-Security_Threat-Document" in ids
    assert "SEQ-sotif_scenario_verification-Hazard-Document" in ids
