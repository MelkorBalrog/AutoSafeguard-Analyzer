import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.governance import GovernanceDiagram


def test_requirement_pattern_generation():
    diagram = GovernanceDiagram()
    diagram.add_task("WP1", node_type="Work Product")
    diagram.add_task("WP2", node_type="Work Product")
    diagram.add_relationship("WP1", "WP2", conn_type="Propagate")

    reqs = diagram.generate_requirements()
    texts = [r[0] if isinstance(r, tuple) else r.text for r in reqs]
    assert any("propagate" in t and "WP2" in t for t in texts)
