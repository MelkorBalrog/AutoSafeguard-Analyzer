import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram, GeneratedRequirement


def test_requirement_rule_subject_overrides_node_roles():
    diagram = GovernanceDiagram()
    diagram.add_task("Source", node_type="Task")
    diagram.add_task("ActorNode", node_type="Role")
    diagram.add_relationship("Source", "ActorNode", label="annotation")

    reqs = [r for r in diagram.generate_requirements() if isinstance(r, GeneratedRequirement)]
    assert any(r.subject == "Engineering team" and r.obj == "ActorNode" and r.action == "annotate" for r in reqs)
