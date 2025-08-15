import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram


def test_generate_requirements_from_governance_diagram():
    diagram = GovernanceDiagram()
    diagram.add_task("Start")
    diagram.add_task("Approve")
    diagram.add_task("Finish")
    diagram.add_flow("Start", "Approve")
    diagram.add_flow("Approve", "Finish", condition="approval granted")
    diagram.add_relationship("Start", "Finish", condition="risk identified")

    reqs = diagram.generate_requirements()
    texts = [t for t, _ in reqs]

    assert "The system shall perform Start." in texts
    assert "Task 'Start' shall precede task 'Approve'." in texts
    assert "If approval granted, Task 'Approve' shall precede task 'Finish'." in texts
    assert "If risk identified, Task 'Start' shall relate to task 'Finish'." in texts

    # Check structured components for one requirement
    start_req = next(r for r in reqs if r.text == "Task 'Start' shall precede task 'Approve'.")
    assert start_req.sub == "Task 'Start'"
    assert start_req.act == "precede"
    assert start_req.obj == "task 'Approve'"
    assert start_req.cnd is None
