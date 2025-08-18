import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLDiagramWindow
from gui.style_manager import StyleManager


def test_governance_shapes_and_relations():
    shape = SysMLDiagramWindow._shape_for_tool
    assert shape(None, "Process") == "hexagon"
    assert shape(None, "Task") == "trapezoid"
    assert shape(None, "Vehicle") == "vehicle"
    assert shape(None, "Approves") == "relation"
    assert shape(None, "Hazard") == "triangle"
    assert shape(None, "Risk Assessment") == "diamond"
    assert shape(None, "Safety Goal") == "pentagon"
    assert shape(None, "Security Threat") == "cross"
    assert shape(None, "Safety Plan") == "document"

    style = StyleManager.get_instance()
    for element in [
        "Hazard",
        "Risk Assessment",
        "Safety Goal",
        "Security Threat",
        "Safety Plan",
    ]:
        assert style.get_color(element) != "#FFFFFF"

