import types

from gui import architecture


def _window():
    win = architecture.GovernanceDiagramWindow.__new__(
        architecture.GovernanceDiagramWindow
    )
    win.repo = types.SimpleNamespace(diagrams={}, relationships=[], active_phase=None)
    win.diagram_id = "d"
    win.repo.diagrams["d"] = types.SimpleNamespace(diag_type="Governance Diagram")
    return win


def test_standard_used_by_phase_valid():
    win = _window()
    src = architecture.SysMLObject(1, "Standard", 0, 0, properties={"name": "STD"})
    dst = architecture.SysMLObject(2, "Lifecycle Phase", 0, 0, properties={"name": "P"})
    valid, _ = architecture.GovernanceDiagramWindow.validate_connection(
        win, src, dst, "Used By"
    )
    assert valid


def test_phase_used_by_standard_invalid():
    win = _window()
    src = architecture.SysMLObject(1, "Lifecycle Phase", 0, 0, properties={"name": "P"})
    dst = architecture.SysMLObject(2, "Standard", 0, 0, properties={"name": "STD"})
    valid, msg = architecture.GovernanceDiagramWindow.validate_connection(
        win, src, dst, "Used By"
    )
    assert not valid
    assert "not allowed" in msg.lower()
