import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram, GeneratedRequirement


def test_requirement_pattern_variables_used():
    diag = GovernanceDiagram()
    diag.add_task("DB", node_type="Database")
    diag.add_task("Acquire", node_type="Data acquisition")
    diag.add_relationship("DB", "Acquire", conn_type="Acquisition")
    reqs = [r for r in diag.generate_requirements() if isinstance(r, GeneratedRequirement)]
    pattern_req = next((r for r in reqs if r.variables), None)
    assert pattern_req is not None
    assert "acceptance_criteria" in pattern_req.variables
