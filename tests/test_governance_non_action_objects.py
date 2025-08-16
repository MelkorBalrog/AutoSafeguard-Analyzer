import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sysml.sysml_repository import SysMLRepository
from analysis.governance import GovernanceDiagram


def test_requirements_with_non_action_objects():
    repo = SysMLRepository.reset_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    ann = repo.create_element("ANN", name="ANN1")
    gate = repo.create_element("Decision", name="Gate")
    diag.objects = [
        {"obj_id": 1, "obj_type": "ANN", "element_id": ann.elem_id, "properties": {"name": "ANN1"}},
        {"obj_id": 2, "obj_type": "Decision", "element_id": gate.elem_id, "properties": {"name": "Gate"}},
    ]
    diag.connections = [
        {"src": 2, "dst": 1, "conn_type": "AI training", "name": "data ready", "properties": {}}
    ]

    gov = GovernanceDiagram.from_repository(repo, diag.diag_id)
    reqs = gov.generate_requirements()
    texts = [r.text for r in reqs]
    assert any("train 'ANN1'" in t for t in texts)
