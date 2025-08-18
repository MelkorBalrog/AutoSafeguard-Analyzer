from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import load_diagram_rules

def _safety_ai_rules():
    cfg_path = Path(__file__).resolve().parents[1] / 'config' / 'diagram_rules.json'
    cfg = load_diagram_rules(cfg_path)
    return cfg.get('connection_rules', {}).get('Governance Diagram', {})

def test_data_acquisition_relation_direction():
    rules = _safety_ai_rules()
    acq = rules.get("Acquisition", {})
    assert acq.get("AI Database") == ["Data acquisition"]
    fr_eval = rules.get("Field risk evaluation", {})
    assert fr_eval.get("AI Database") == ["Data acquisition"]
    fd_collect = rules.get("Field data collection", {})
    assert fd_collect.get("AI Database") == ["Data acquisition", "Task"]


def test_curation_process_data():
    rules = _safety_ai_rules()
    cur = rules.get("Curation", {})
    assert cur.get("Process") == ["Data"]
