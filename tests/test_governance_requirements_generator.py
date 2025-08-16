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
    texts = [r.text for r in reqs]

    assert "Data Steward shall perform 'Review Data'." in texts
    assert "Review Data shall produce 'Report'." in texts
    assert "If data validated, Data Steward shall approve 'Report'." in texts
    assert "Review Data shall comply with 'Policy DP-001'." in texts
    assert "Organization shall review data." in texts

    perf_req = next(r for r in reqs if r.action == "perform")
    assert perf_req.subject == "Data Steward"
    assert perf_req.obj == "Review Data"

    approve_req = next(r for r in reqs if r.action == "approve")
    assert approve_req.condition == "data validated"
    assert approve_req.subject == "Data Steward"
    assert approve_req.obj == "Report"
    review_req = next(r for r in reqs if r.action == "review data")
    assert review_req.subject == "Organization"
    assert review_req.req_type == "organizational"

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
    texts = [r.text for r in reqs]
    assert "If completion >= 0.98, Engineering team shall train 'ANN1'." in texts
    assert "If completion < 0.98, Engineering team shall curate 'Database1'." in texts

    train_req = next(r for r in reqs if r.action == "train")
    assert train_req.subject == "Engineering team"
    assert train_req.obj == "ANN1"
    assert train_req.condition == "completion >= 0.98"

    curate_req = next(r for r in reqs if r.action == "curate")
    assert curate_req.subject == "Engineering team"
    assert curate_req.obj == "Database1"
    assert curate_req.condition == "completion < 0.98"


def test_data_acquisition_compartment_sources():
    diagram = GovernanceDiagram()
    diagram.add_task(
        "Acquire Data",
        node_type="Data acquisition",
        compartments=["Sensor A", "Sensor B"],
    )

    reqs = diagram.generate_requirements()
    texts = [r.text for r in reqs]

    assert "Engineering team shall acquire data from 'Sensor A'." in texts
    assert "Engineering team shall acquire data from 'Sensor B'." in texts

    data_reqs = [r for r in reqs if r.action == "acquire data from"]
    assert all(r.req_type == "AI safety" for r in data_reqs)
    assert all(r.subject == "Engineering team" for r in data_reqs)
    assert {r.obj for r in data_reqs} == {"Sensor A", "Sensor B"}


def test_tasks_create_requirement_actions():
    diagram = GovernanceDiagram()
    diagram.add_task("Review Data", node_type="Activity")
    diagram.add_task("Acquire Data", node_type="Data acquisition")

    reqs = diagram.generate_requirements()
    texts = [r.text for r in reqs]

    assert "Organization shall review data." in texts
    assert "Engineering team shall acquire data." in texts

    review_req = next(r for r in reqs if r.action == "review data")
    assert review_req.subject == "Organization"
    assert review_req.req_type == "organizational"
    acquire_req = next(r for r in reqs if r.action == "acquire data")
    assert acquire_req.subject == "Engineering team"
    assert acquire_req.req_type == "AI safety"
