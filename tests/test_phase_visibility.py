from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule

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
