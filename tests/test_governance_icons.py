import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLDiagramWindow


def test_governance_shapes_and_relations():
    shape = SysMLDiagramWindow._shape_for_tool
    assert shape(None, "Process") == "hexagon"
    assert shape(None, "Task") == "trapezoid"
    assert shape(None, "Vehicle") == "vehicle"
    assert shape(None, "Approves") == "relation"

