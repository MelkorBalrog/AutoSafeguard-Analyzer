from sysml.sysml_repository import SysMLRepository, SysMLDiagram
from gui.architecture import SysMLDiagramWindow, SysMLObject
import gui.architecture as arch


def test_trace_relation_respects_config():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    diag = SysMLDiagram(diag_id="d", diag_type="Governance Diagram")
    repo.diagrams["d"] = diag

    wp = SysMLObject(1, "Work Product", 0, 0, properties={"name": "WP"})
    phase = SysMLObject(2, "Lifecycle Phase", 100, 0, properties={"name": "Phase"})
    diag.objects = [wp, phase]

    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.repo = repo
    win.diagram_id = "d"
    win.connections = []
    win.objects = diag.objects

    rules = arch.CONNECTION_RULES.setdefault("Governance Diagram", {})
    orig = rules.get("Trace")
    rules["Trace"] = {"Work Product": {"Lifecycle Phase"}}
    try:
        valid, msg = SysMLDiagramWindow.validate_connection(win, wp, phase, "Trace")
        assert valid, msg
    finally:
        if orig is None:
            del rules["Trace"]
        else:
            rules["Trace"] = orig


def test_reuse_relation_respects_config():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    diag = SysMLDiagram(diag_id="d", diag_type="Governance Diagram")
    repo.diagrams["d"] = diag

    src = SysMLObject(1, "Work Product", 0, 0, properties={"name": "A"})
    dst = SysMLObject(2, "Work Product", 100, 0, properties={"name": "B"})
    diag.objects = [src, dst]

    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.repo = repo
    win.diagram_id = "d"
    win.connections = []
    win.objects = diag.objects

    rules = arch.CONNECTION_RULES.setdefault("Governance Diagram", {})
    orig = rules.get("Re-use")
    rules["Re-use"] = {"Work Product": {"Work Product"}}
    try:
        valid, msg = SysMLDiagramWindow.validate_connection(win, src, dst, "Re-use")
        assert valid, msg
    finally:
        if orig is None:
            del rules["Re-use"]
        else:
            rules["Re-use"] = orig
