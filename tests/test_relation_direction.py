from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import load_diagram_rules

def _safety_ai_rules():
    cfg_path = Path(__file__).resolve().parents[1] / 'config' / 'diagram_rules.json'
    cfg = load_diagram_rules(cfg_path)
    return cfg.get('safety_ai_relation_rules', {})

def test_data_acquisition_relation_direction():
    rules = _safety_ai_rules()
    expected = {"Database": ["Data acquisition"]}
    assert rules.get("Acquisition") == expected
    assert rules.get("Field risk evaluation") == expected
    expected_collect = {"Database": ["Data acquisition", "Task"]}
    assert rules.get("Field data collection") == expected_collect
