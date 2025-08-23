import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp

def test_shared_malfunction_across_analyses():
    app = AutoMLApp.__new__(AutoMLApp)
    te1 = type("N", (), {"unique_id": 1, "user_name": "F", "description": "d", "malfunction": "m"})()
    te2 = type("N", (), {"unique_id": 2, "user_name": "C", "description": "d2", "malfunction": "m"})()
    app.top_events = [te1]
    app.cta_events = [te2]
    app.paa_events = []
    app._update_shared_product_goals()
    assert te1.name_readonly and te2.name_readonly
    assert te1.description == te2.description
    assert te1.product_goal is te2.product_goal
