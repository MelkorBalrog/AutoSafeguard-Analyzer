import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp, FaultTreeNode


def test_malfunction_duplicate_same_analysis():
    app = AutoMLApp.__new__(AutoMLApp)
    te1 = FaultTreeNode("", "TOP EVENT")
    te1.malfunction = "M"
    te2 = FaultTreeNode("", "TOP EVENT")
    te2.malfunction = "M"
    app.top_events = [te1, te2]
    assert app.is_duplicate_malfunction(te2, "M")
    app.cta_events = [te2]
    app.top_events = [te1]
    assert not app.is_duplicate_malfunction(te2, "M")
