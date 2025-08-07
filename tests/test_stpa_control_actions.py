import types
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis.models import StpaDoc
from gui.stpa_window import StpaWindow
from gui.architecture import SysMLObject, DiagramConnection
from sysml.sysml_repository import SysMLRepository


def test_get_control_actions_returns_only_control_action_connections():
    repo = SysMLRepository.reset_instance()
    e1 = repo.create_element("Block", name="A")
    e2 = repo.create_element("Block", name="B")
    act = repo.create_element("Action", name="Do")
    diag = repo.create_diagram("Control Flow Diagram", name="CF")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Existing Element", 0, 0, element_id=e1.elem_id)
    o2 = SysMLObject(2, "Existing Element", 0, 100, element_id=e2.elem_id)
    diag.objects = [o1.__dict__, o2.__dict__]
    ca_conn = DiagramConnection(o1.obj_id, o2.obj_id, "Control Action", element_id=act.elem_id)
    fb_conn = DiagramConnection(o2.obj_id, o1.obj_id, "Feedback")
    diag.connections = [ca_conn.__dict__, fb_conn.__dict__]

    app = types.SimpleNamespace(active_stpa=StpaDoc("doc", diag.diag_id, []))
    window = StpaWindow.__new__(StpaWindow)
    window.app = app

    labels = window._get_control_actions()
    assert labels == ["<<control action>> Do"]


def test_get_control_actions_from_relationship_stereotype():
    repo = SysMLRepository.reset_instance()
    e1 = repo.create_element("Block", name="A")
    e2 = repo.create_element("Block", name="B")
    act = repo.create_element("Action", name="Do")
    diag = repo.create_diagram("Control Flow Diagram", name="CF")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Existing Element", 0, 0, element_id=e1.elem_id)
    o2 = SysMLObject(2, "Existing Element", 0, 100, element_id=e2.elem_id)
    diag.objects = [o1.__dict__, o2.__dict__]
    rel = repo.create_relationship(
        "Connector",
        e1.elem_id,
        e2.elem_id,
        stereotype="control action",
        properties={"element_id": act.elem_id},
    )
    diag.relationships = [rel.rel_id]
    diag.connections = []

    app = types.SimpleNamespace(active_stpa=StpaDoc("doc", diag.diag_id, []))
    window = StpaWindow.__new__(StpaWindow)
    window.app = app

    labels = window._get_control_actions()
    assert labels == ["<<control action>> Do"]


def test_diagram_lookup_prefers_control_flow_diagrams():
    repo = SysMLRepository.reset_instance()
    e1 = repo.create_element("Block", name="A")
    e2 = repo.create_element("Block", name="B")
    act = repo.create_element("Action", name="Do")
    # Create diagrams with the same base name but different types
    activity = repo.create_diagram("Activity Diagram", name="Same")
    cf = repo.create_diagram("Control Flow Diagram", name="Same")

    # Add elements and a control action connection to the control flow diagram
    repo.add_element_to_diagram(cf.diag_id, e1.elem_id)
    repo.add_element_to_diagram(cf.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Existing Element", 0, 0, element_id=e1.elem_id)
    o2 = SysMLObject(2, "Existing Element", 0, 100, element_id=e2.elem_id)
    cf.objects = [o1.__dict__, o2.__dict__]
    ca_conn = DiagramConnection(o1.obj_id, o2.obj_id, "Control Action", element_id=act.elem_id)
    cf.connections = [ca_conn.__dict__]

    # Prepare StpaWindow instance with stubbed dialogs and widgets
    app = types.SimpleNamespace(
        stpa_docs=[],
        active_stpa=None,
        stpa_entries=[],
        update_views=lambda: None,
    )
    window = StpaWindow.__new__(StpaWindow)
    window.app = app
    window.refresh_docs = lambda: None
    window.refresh = lambda: None
    window.diag_lbl = types.SimpleNamespace(config=lambda **kwargs: None)

    class DummyNewDialog:
        def __init__(self, parent, app):
            self.result = ("doc", cf.diag_id)

    window.NewStpaDialog = DummyNewDialog
    window.new_doc()
    assert window.app.active_stpa.diagram == cf.diag_id
    assert window._get_control_actions() == ["<<control action>> Do"]

    # Change to the activity diagram and ensure edit_doc switches back to the CF diagram
    window.app.active_stpa.diagram = activity.diag_id

    class DummyEditDialog:
        def __init__(self, parent, app):
            self.result = cf.diag_id

    window.EditStpaDialog = DummyEditDialog
    window.edit_doc()
    assert window.app.active_stpa.diagram == cf.diag_id
    assert window._get_control_actions() == ["<<control action>> Do"]


def test_get_control_actions_ignores_non_cfd_diagrams():
    repo = SysMLRepository.reset_instance()
    e1 = repo.create_element("Block", name="A")
    e2 = repo.create_element("Block", name="B")
    act = repo.create_element("Action", name="Do")
    diag = repo.create_diagram("Activity Diagram", name="Act")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Existing Element", 0, 0, element_id=e1.elem_id)
    o2 = SysMLObject(2, "Existing Element", 0, 100, element_id=e2.elem_id)
    diag.objects = [o1.__dict__, o2.__dict__]
    ca_conn = DiagramConnection(o1.obj_id, o2.obj_id, "Control Action", element_id=act.elem_id)
    diag.connections = [ca_conn.__dict__]

    app = types.SimpleNamespace(active_stpa=StpaDoc("doc", diag.diag_id, []))
    window = StpaWindow.__new__(StpaWindow)
    window.app = app

    assert window._get_control_actions() == []
