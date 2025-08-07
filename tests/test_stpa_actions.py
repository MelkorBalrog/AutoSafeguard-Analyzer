import types
from gui.stpa_window import StpaWindow
from analysis.models import StpaDoc
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


def reset_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


def test_get_actions_returns_control_actions():
    repo = reset_repo()
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


def test_get_actions_ignores_extra_connection_fields():
    repo = reset_repo()
    diag = SysMLDiagram(diag_id="d1", diag_type="Control Flow Diagram")
    diag.objects = [
        {"obj_id": 1, "name": "Controller"},
        {"obj_id": 2, "name": "Process"},
    ]
    diag.connections = [
        {
            "src": 1,
            "dst": 2,
            "conn_type": "Control Action",
            "name": "Act",
            "id": 123,
        }
    ]
    repo.diagrams[diag.diag_id] = diag
    app = types.SimpleNamespace(active_stpa=StpaDoc("Doc", diag.diag_id, []))
    win = StpaWindow.__new__(StpaWindow)
    win.app = app
    actions = win._get_actions()
    assert actions == ["Act"]


def test_get_actions_matches_diagram_by_name():
    repo = reset_repo()
    diag = SysMLDiagram(diag_id="d1", diag_type="Control Flow Diagram", name="CF")
    diag.objects = [
        {"obj_id": 1, "name": "Controller"},
        {"obj_id": 2, "name": "Process"},
    ]
    diag.connections = [
        {"src": 1, "dst": 2, "conn_type": "Control Action", "name": "Act"},
    ]
    repo.diagrams[diag.diag_id] = diag
    app = types.SimpleNamespace(active_stpa=StpaDoc("Doc", diag.name, []))
    win = StpaWindow.__new__(StpaWindow)
    win.app = app
    actions = win._get_actions()
    assert actions == ["Act"]
