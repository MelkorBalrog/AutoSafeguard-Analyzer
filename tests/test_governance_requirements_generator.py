import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram


def test_generate_requirements_from_governance_diagram():
    diagram = GovernanceDiagram()
    diagram.add_task("Data Steward", node_type="Role")
    diagram.add_task("Review Data", node_type="Activity")
    diagram.add_task("Report", node_type="Document")
    diagram.add_task("Policy DP-001", node_type="Policy")
    diagram.add_relationship("Data Steward", "Review Data", label="performs")
    diagram.add_relationship("Review Data", "Report", label="produces")
    diagram.add_relationship(
        "Data Steward", "Report", label="approves", condition="data validated"
    )
    diagram.add_relationship("Review Data", "Policy DP-001", label="governed by")

    reqs = diagram.generate_requirements()
    texts = [t for t, _ in reqs]

    assert "Data Steward shall perform 'Review Data'." in texts
    assert "Review Data shall produce 'Report'." in texts
    assert "If data validated, Data Steward shall approve 'Report'." in texts
    assert "Review Data shall comply with 'Policy DP-001'." in texts


def test_ai_training_and_curation_requirements():
    diagram = GovernanceDiagram()
    diagram.add_task("Decision1", node_type="Decision")
    diagram.add_task("ANN1", node_type="ANN")
    diagram.add_task("Database1", node_type="Database")
    diagram.add_relationship(
        "Decision1",
        "ANN1",
        condition="completion >= 0.98",
        conn_type="AI training",
    )
    diagram.add_relationship(
        "Decision1",
        "Database1",
        condition="completion < 0.98",
        conn_type="Curation",
    )
    reqs = diagram.generate_requirements()
    texts = [t for t, _ in reqs]
    assert "If completion >= 0.98, Engineering team shall train 'ANN1'." in texts
    assert "If completion < 0.98, Engineering team shall curate 'Database1'." in texts
