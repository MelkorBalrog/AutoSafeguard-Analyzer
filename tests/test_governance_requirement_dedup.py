from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram


def test_data_acquisition_default_requirement_removed_when_sources_present():
    diagram = GovernanceDiagram()
    diagram.add_task(
        "Acquire Data",
        node_type="Data acquisition",
        compartments=["Sensor A"],
    )

    reqs = diagram.generate_requirements()
    texts = [r.text if hasattr(r, "text") else r[0] for r in reqs]

    assert "Engineering team shall acquire data from 'Sensor A'." in texts
    assert "Engineering team shall acquire data." not in texts
    assert sum("acquire data" in t for t in texts) == 1
