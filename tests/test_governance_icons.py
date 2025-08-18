import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLDiagramWindow
from gui.style_manager import StyleManager


def test_governance_shapes_and_relations():
    shape = SysMLDiagramWindow._shape_for_tool
    assert shape(None, "Task") == "trapezoid"
    assert shape(None, "Vehicle") == "vehicle"
    assert shape(None, "Approves") == "relation"
    assert shape(None, "Hazard") == "hazard"
    assert shape(None, "Risk Assessment") == "clipboard"
    assert shape(None, "Safety Goal") == "shield"
    assert shape(None, "Security Threat") == "bug"
    assert shape(None, "Organization") == "building"
    assert shape(None, "Business Unit") == "department"
    assert shape(None, "Policy") == "scroll"
    assert shape(None, "Principle") == "scale"
    assert shape(None, "Guideline") == "compass"
    assert shape(None, "Standard") == "ribbon"
    assert shape(None, "Metric") == "chart"
    assert shape(None, "Safety Compliance") == "shield_check"
    assert shape(None, "Process") == "gear"
    assert shape(None, "Operation") == "wrench"
    assert shape(None, "Driving Function") == "steering"
    assert shape(None, "Plan") == "document"
    assert shape(None, "Data") == "cylinder"
    assert shape(None, "Field Data") == "cylinder"

    style = StyleManager.get_instance()
    for element in [
        "Hazard",
        "Risk Assessment",
        "Safety Goal",
        "Security Threat",
        "Organization",
        "Business Unit",
        "Policy",
        "Principle",
        "Guideline",
        "Standard",
        "Metric",
        "Safety Compliance",
        "Process",
        "Operation",
        "Driving Function",
        "Plan",
        "Data",
        "Field Data",
    ]:
        assert style.get_color(element) != "#FFFFFF"
