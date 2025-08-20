import types
from gui import architecture


def test_role_executes_operation_connection():
    win = architecture.GovernanceDiagramWindow.__new__(
        architecture.GovernanceDiagramWindow
    )
    win.repo = types.SimpleNamespace(diagrams={})
    win.diagram_id = "d"
    win.repo.diagrams["d"] = types.SimpleNamespace(diag_type="Governance Diagram")
    src = architecture.SysMLObject(1, "Role", 0, 0)
    dst = architecture.SysMLObject(2, "Operation", 0, 0)
    valid, _ = architecture.GovernanceDiagramWindow.validate_connection(
        win, src, dst, "Executes"
    )
    assert valid
