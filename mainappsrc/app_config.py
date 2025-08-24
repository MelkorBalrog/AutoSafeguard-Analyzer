from pathlib import Path

from config import load_diagram_rules, load_report_template
from analysis.requirement_rule_generator import regenerate_requirement_patterns

_CONFIG_PATH = Path(__file__).resolve().parent / "config/diagram_rules.json"
_CONFIG = load_diagram_rules(_CONFIG_PATH)
GATE_NODE_TYPES = set(_CONFIG.get("gate_node_types", []))
_PATTERN_PATH = Path(__file__).resolve().parent / "config/requirement_patterns.json"
_REPORT_TEMPLATE_PATH = Path(__file__).resolve().parent / "config/product_report_template.json"

VALID_SUBTYPES = {
    "Confidence": ["Function", "Human Task"],
    "Robustness": ["Function", "Human Task"],
    "Maturity": ["Functionality"],
    "Rigor": ["Failure", "AI Error", "Functional Insufficiency"],
    "Prototype Assurance Level (PAL)": ["Vehicle Level Function"],
}

PMHF_TARGETS = {
    "D": 1e-8,
    "C": 1e-7,
    "B": 1e-7,
    "A": 1e-6,
    "QM": 1.0,
}


def reload_local_config() -> None:
    """Reload gate node types from the external configuration file."""
    global _CONFIG, GATE_NODE_TYPES
    _CONFIG = load_diagram_rules(_CONFIG_PATH)
    GATE_NODE_TYPES = set(_CONFIG.get("gate_node_types", []))
    regenerate_requirement_patterns()

__all__ = [
    "GATE_NODE_TYPES",
    "_CONFIG",
    "_CONFIG_PATH",
    "_PATTERN_PATH",
    "_REPORT_TEMPLATE_PATH",
    "VALID_SUBTYPES",
    "PMHF_TARGETS",
    "reload_local_config",
]
