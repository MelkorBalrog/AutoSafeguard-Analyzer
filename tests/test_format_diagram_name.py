from gui.architecture import format_diagram_name
from sysml.sysml_repository import SysMLDiagram


def test_format_diagram_name_adds_abbreviation():
    diag = SysMLDiagram("d1", "Control Flow Diagram", name="Diag")
    assert format_diagram_name(diag) == "Diag : CFD"


def test_format_diagram_name_ibd():
    diag = SysMLDiagram("d2", "Internal Block Diagram", name="Struct")
    assert format_diagram_name(diag) == "Struct : IBD"

