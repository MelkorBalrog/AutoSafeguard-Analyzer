import types
from gui.stpa_window import StpaWindow
from analysis.models import StpaDoc
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


def test_get_actions_returns_control_actions():
    repo = SysMLRepository.get_instance()
    diag = SysMLDiagram(diag_id="d1", diag_type="Control Flow Diagram")
    diag.objects = [
        {"obj_id": 1, "name": "Controller"},
        {"obj_id": 2, "name": "Process"},
    ]
    diag.connections = [
        {"src": 1, "dst": 2, "conn_type": "Control Action", "name": "Act"},
        {"src": 2, "dst": 1, "conn_type": "Feedback", "name": "FB"},
    ]
    repo.diagrams[diag.diag_id] = diag
    app = types.SimpleNamespace(active_stpa=StpaDoc("Doc", diag.diag_id, []))
    win = StpaWindow.__new__(StpaWindow)
    win.app = app
    actions = win._get_actions()
    assert actions == ["Act"]
