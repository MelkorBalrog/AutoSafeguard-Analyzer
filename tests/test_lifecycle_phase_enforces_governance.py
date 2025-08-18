from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository

def test_diagram_and_elements_hidden_without_phase():
    repo = SysMLRepository.reset_instance()
    # create diagram and element before any lifecycle phase is active
    diag = repo.create_diagram("Control Flow Diagram", name="CF")
    elem = repo.create_element("Block", name="B1")
    repo.add_element_to_diagram(diag.diag_id, elem.elem_id)
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1"), GovernanceModule("P2")]
    # activate first phase
    toolbox.set_active_module("P1")
    # diagram and element were created without a phase, so they should now be hidden
    assert not repo.diagram_visible(diag.diag_id)
    assert diag.diag_id not in repo.visible_diagrams()
    assert elem.elem_id not in repo.visible_elements()
    # document visibility is also blocked
    assert not toolbox.document_visible("Control Flow Diagram", diag.name)

