import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram


def _texts(reqs):
    texts = []
    for r in reqs:
        if isinstance(r, tuple):
            texts.append(r[0])
        elif hasattr(r, "text"):
            texts.append(r.text)
        else:
            texts.append(str(r))
    return texts


def test_phase_transition_requirement_direct_flow():
    diagram = GovernanceDiagram()
    diagram.add_task("P1", node_type="Lifecycle Phase")
    diagram.add_task("P2", node_type="Lifecycle Phase")
    diagram.add_flow("P1", "P2")

    reqs = diagram.generate_requirements()
    texts = _texts(reqs)
    assert "P1 shall transition to 'P2'." in texts


def test_phase_transition_requirement_with_reuse_and_condition():
    diagram = GovernanceDiagram()
    diagram.add_task("P1", node_type="Lifecycle Phase")
    diagram.add_task("P2", node_type="Lifecycle Phase")
    diagram.add_flow("P1", "P2", "design approved")
    diagram.add_relationship("P2", "P1", conn_type="Re-use")

    reqs = diagram.generate_requirements()
    texts = _texts(reqs)
    assert (
        "P1 shall transition to 'P2' reusing outputs from 'P1' only after design approved." in texts
    )
