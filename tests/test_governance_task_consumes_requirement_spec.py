import types

from gui import architecture


def test_task_consumes_requirement_specification():
    """Tasks should consume Requirement Specification work products."""
    architecture.reload_config()
    win = architecture.GovernanceDiagramWindow.__new__(architecture.GovernanceDiagramWindow)
    win.repo = types.SimpleNamespace(diagrams={})
    win.diagram_id = "d"
    win.repo.diagrams["d"] = types.SimpleNamespace(diag_type="Governance Diagram")
    src = architecture.SysMLObject(1, "Action", 0, 0)
    dst = architecture.SysMLObject(2, "Work Product", 0, 0, properties={"name": "Requirement Specification"})
    valid, _ = architecture.GovernanceDiagramWindow.validate_connection(win, src, dst, "Consumes")
    assert valid
