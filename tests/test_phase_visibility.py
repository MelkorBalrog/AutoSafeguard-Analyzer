from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from dataclasses import asdict
from gui.architecture import SysMLObject, DiagramConnection

def test_elements_follow_phase_visibility():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1"), GovernanceModule("P2")]
    toolbox.set_active_module("P1")
    elem = repo.create_element("Block")
    assert repo.element_visible(elem.elem_id)
    assert elem.phase == "P1"
    visible = set(repo.visible_elements().keys())
    assert elem.elem_id in visible
    toolbox.set_active_module("P2")
    assert not repo.element_visible(elem.elem_id)
    visible = set(repo.visible_elements().keys())
    assert elem.elem_id not in visible
    toolbox.set_active_module("P1")
    assert repo.element_visible(elem.elem_id)
    visible = set(repo.visible_elements().keys())
    assert elem.elem_id in visible


def test_diagram_objects_and_connections_follow_phase_visibility():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1"), GovernanceModule("P2")]
    toolbox.set_active_module("P1")
    diag = repo.create_diagram("Block Definition Diagram")
    obj = SysMLObject(1, "Block", 0.0, 0.0)
    diag.objects.append(asdict(obj))
    conn = DiagramConnection(1, 2, "Association")
    diag.connections.append(asdict(conn))
    assert repo.visible_objects(diag.diag_id)
    assert repo.visible_connections(diag.diag_id)
    toolbox.set_active_module("P2")
    assert not repo.visible_objects(diag.diag_id)
    assert not repo.visible_connections(diag.diag_id)
    toolbox.set_active_module("P1")
    assert repo.visible_objects(diag.diag_id)
    assert repo.visible_connections(diag.diag_id)
