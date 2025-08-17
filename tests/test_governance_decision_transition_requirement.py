import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram


def test_decision_transition_requirement_mentions_source():
    diagram = GovernanceDiagram()
    diagram.add_task("Collect Data", node_type="Activity")
    diagram.add_task("Decision1", node_type="Decision")
    diagram.add_task("ANN1", node_type="ANN")
    diagram.add_flow("Collect Data", "Decision1")
    diagram.add_relationship(
        "Decision1",
        "ANN1",
        conn_type="AI training",
        condition="completion >= 0.98",
    )

    reqs = diagram.generate_requirements()
    texts = [r.text for r in reqs]
    assert "If completion >= 0.98, after 'Collect Data (Activity)', Engineering team shall train 'ANN1 (ANN)'." in texts
    assert all("Decision1" not in t for t in texts)
