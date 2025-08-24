from mainappsrc.models.sysml.sysml_repository import SysMLRepository, GLOBAL_PHASE


def test_global_phase_assigned_to_new_items():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.active_phase = GLOBAL_PHASE
    elem = repo.create_element("Block", name="E")
    diag = repo.create_diagram("Block Diagram", name="D")
    rel = repo.create_relationship("Association", elem.elem_id, elem.elem_id)
    assert elem.phase == GLOBAL_PHASE
    assert diag.phase == GLOBAL_PHASE
    assert rel.phase == GLOBAL_PHASE


def test_set_diagram_phase_propagates_to_contents():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.active_phase = GLOBAL_PHASE
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    elem = repo.create_element("Action", name="A")
    repo.add_element_to_diagram(diag.diag_id, elem.elem_id)
    obj = {"id": 1, "element_id": elem.elem_id}
    diag.objects.append(obj)
    repo.set_diagram_phase(diag.diag_id, "P1")
    assert diag.phase == "P1"
    assert repo.elements[elem.elem_id].phase == "P1"
    assert diag.objects[0]["phase"] == "P1"
    repo.active_phase = "P1"
    assert repo.object_visible(diag.objects[0], diag.diag_id)
