import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram, GeneratedRequirement


@pytest.mark.parametrize(
    "conn_type, action",
    [
        ("Re-use", "re-use"),
        ("Propagate", "propagate"),
        ("Propagate by Review", "propagate by review"),
        ("Propagate by Approval", "propagate by approval"),
        ("Used By", "be used by"),
        ("Used after Review", "be used after review"),
        ("Used after Approval", "be used after approval"),
        ("Trace", "trace to"),
        ("Satisfied by", "be satisfied by"),
        ("Derived from", "be derived from"),
    ],
)
def test_generate_requirements_for_additional_relationships(conn_type, action):
    diagram = GovernanceDiagram()
    diagram.add_task("Source")
    diagram.add_task("Target")
    diagram.add_relationship("Source", "Target", conn_type=conn_type)

    reqs = [r for r in diagram.generate_requirements() if isinstance(r, GeneratedRequirement)]
    assert any(r.action == action for r in reqs)
