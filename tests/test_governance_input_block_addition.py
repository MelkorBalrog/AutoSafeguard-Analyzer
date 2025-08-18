import types
import pytest
from sysml.sysml_repository import SysMLRepository
from analysis import safety_management as sm


@pytest.mark.parametrize("target", ["Control Flow Diagram", "HAZOP", "Risk Assessment"])
def test_existing_elements_require_governance(target):
    repo = SysMLRepository.reset_instance()
    arch = repo.create_diagram("Architecture Diagram", name="AD")
    elem = repo.create_element("Block", name="B1")
    repo.add_element_to_diagram(arch.diag_id, elem.elem_id)
    repo.link_diagram(elem.elem_id, arch.diag_id)
    tgt = repo.create_diagram(target, name="T")

    toolbox = types.SimpleNamespace(analysis_inputs=lambda t, **k: set())
    sm.ACTIVE_TOOLBOX = toolbox

    repo.add_element_to_diagram(tgt.diag_id, elem.elem_id)
    assert elem.elem_id not in tgt.elements

    toolbox.analysis_inputs = lambda t, **k: {"Architecture Diagram"}
    repo.add_element_to_diagram(tgt.diag_id, elem.elem_id)
    assert elem.elem_id in tgt.elements

    sm.ACTIVE_TOOLBOX = None
