import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram


def test_label_relationship_between_database_nodes():
    diagram = GovernanceDiagram()
    diagram.add_task("User DB")
    diagram.add_task("Analytics DB")
    diagram.add_relationship("User DB", "Analytics DB", label="sync with")

    assert diagram.edge_data[("User DB", "Analytics DB")]["label"] == "sync with"

    reqs = diagram.generate_requirements()
    assert "Task 'User DB' shall sync with task 'Analytics DB'." in reqs
