import types
from gui.stpa_window import StpaWindow
from analysis.models import StpaDoc
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


def reset_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


def test_get_control_actions_returns_control_actions_only():
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
    actions = win._get_control_actions()
    assert actions == ["Act"]


def test_get_control_actions_ignores_extra_connection_fields():
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
    actions = win._get_control_actions()
    assert actions == ["Act"]


def test_get_control_actions_matches_diagram_by_name():
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
    actions = win._get_control_actions()
    assert actions == ["Act"]


def test_get_control_actions_recurses_into_linked_diagrams():
    repo = reset_repo()
    # Top-level diagram with a control action and an object linked to a subdiagram
    diag1 = SysMLDiagram(diag_id="d1", diag_type="Control Flow Diagram")
    elem = repo.create_element("ActionUsage", name="Sub")
    diag1.objects = [
        {"obj_id": 1, "name": "Controller"},
        {"obj_id": 2, "name": "Process"},
        {"obj_id": 3, "element_id": elem.elem_id},
    ]
    diag1.connections = [
        {"src": 1, "dst": 2, "conn_type": "Control Action", "name": "Act"},
    ]

    # Subdiagram linked from elem with another control action
    diag2 = SysMLDiagram(diag_id="d2", diag_type="Control Flow Diagram")
    diag2.objects = [
        {"obj_id": 10, "name": "SubController"},
        {"obj_id": 11, "name": "SubProcess"},
    ]
    diag2.connections = [
        {"src": 10, "dst": 11, "conn_type": "Control Action", "name": "SubAct"},
    ]

    repo.diagrams[diag1.diag_id] = diag1
    repo.diagrams[diag2.diag_id] = diag2
    repo.link_diagram(elem.elem_id, diag2.diag_id)

    app = types.SimpleNamespace(active_stpa=StpaDoc("Doc", diag1.diag_id, []))
    win = StpaWindow.__new__(StpaWindow)
    win.app = app
    actions = win._get_control_actions()
    assert actions == ["Act", "SubAct"]


def test_get_control_actions_recurses_from_connection_links():
    repo = reset_repo()
    # Top-level diagram with a non-control connection linked to a subdiagram
    diag1 = SysMLDiagram(diag_id="d1", diag_type="Control Flow Diagram")
    elem = repo.create_element("ActionUsage", name="Sub")
    diag1.objects = [
        {"obj_id": 1, "name": "Controller"},
        {"obj_id": 2, "name": "Process"},
    ]
    diag1.connections = [
        {"src": 1, "dst": 2, "conn_type": "Feedback", "element_id": elem.elem_id},
    ]

    # Subdiagram linked from the connection with a control action
    diag2 = SysMLDiagram(diag_id="d2", diag_type="Control Flow Diagram")
    diag2.objects = [
        {"obj_id": 10, "name": "SubController"},
        {"obj_id": 11, "name": "SubProcess"},
    ]
    diag2.connections = [
        {"src": 10, "dst": 11, "conn_type": "Control Action", "name": "SubAct"},
    ]

    repo.diagrams[diag1.diag_id] = diag1
    repo.diagrams[diag2.diag_id] = diag2
    repo.link_diagram(elem.elem_id, diag2.diag_id)

    app = types.SimpleNamespace(active_stpa=StpaDoc("Doc", diag1.diag_id, []))
    win = StpaWindow.__new__(StpaWindow)
    win.app = app
    actions = win._get_control_actions()
    assert actions == ["SubAct"]
