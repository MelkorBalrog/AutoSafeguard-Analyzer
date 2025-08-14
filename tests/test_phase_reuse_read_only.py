from dataclasses import asdict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLObject, DiagramConnection, rename_block, rename_port
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository


def _setup_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


def _prepare():
    repo = _setup_repo()
    gov = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov"]), GovernanceModule(name="P2")]
    toolbox.diagrams = {"Gov": gov.diag_id}
    src = SysMLObject(1, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P1"})
    dst = SysMLObject(2, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P2"})
    gov.objects.extend([asdict(src), asdict(dst)])
    conn = DiagramConnection(dst.obj_id, src.obj_id, "Re-use")
    gov.connections.append(asdict(conn))
    return repo, toolbox


def test_reused_element_read_only_blocks_modification():
    repo, toolbox = _prepare()
    toolbox.set_active_module("P1")
    blk = repo.create_element("Block", name="B1")
    port_elem = repo.create_element("Port", name="p", owner=blk.elem_id)
    block_obj = SysMLObject(1, "Block", 0.0, 0.0, element_id=blk.elem_id, properties={"name": "B1"})
    port_obj = SysMLObject(2, "Port", 0.0, 0.0, element_id=port_elem.elem_id, properties={"name": "p", "parent": str(block_obj.obj_id)})
    toolbox.set_active_module("P2")

    assert repo.element_read_only(blk.elem_id)
    assert repo.element_read_only(port_elem.elem_id)

    rename_block(repo, blk.elem_id, "B2")
    rename_port(repo, port_obj, [block_obj, port_obj], "q")
    assert repo.elements[blk.elem_id].name == "B1"
    assert repo.elements[port_elem.elem_id].name == "p"

    repo.delete_element(blk.elem_id)
    assert blk.elem_id in repo.elements


def test_reused_diagram_read_only_blocks_modification():
    repo, toolbox = _prepare()
    toolbox.set_active_module("P1")
    diag = repo.create_diagram("Block Definition Diagram", name="D1")
    toolbox.diagrams["D1"] = diag.diag_id
    toolbox.set_active_module("P2")

    assert repo.diagram_read_only(diag.diag_id)

    toolbox.rename_diagram("D1", "D2")
    assert repo.diagrams[diag.diag_id].name == "D1"
    assert "D1" in toolbox.diagrams

    toolbox.delete_diagram("D1")
    assert diag.diag_id in repo.diagrams
    assert "D1" in toolbox.diagrams


def _prepare_product_reuse():
    repo = _setup_repo()
    gov = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov"]), GovernanceModule(name="P2")]
    toolbox.diagrams = {"Gov": gov.diag_id}
    phase = SysMLObject(1, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P2"})
    wp = SysMLObject(2, "Work Product", 0.0, 0.0, properties={"name": "FMEA"})
    gov.objects.extend([asdict(phase), asdict(wp)])
    conn = DiagramConnection(phase.obj_id, wp.obj_id, "Re-use")
    gov.connections.append(asdict(conn))
    return repo, toolbox


def test_reused_work_product_read_only_blocks_modification():
    repo, toolbox = _prepare_product_reuse()
    toolbox.set_active_module("P1")
    diag = repo.create_diagram("FMEA", name="F1")
    toolbox.diagrams["F1"] = diag.diag_id
    blk = repo.create_element("Block", name="B1")
    repo.link_diagram(blk.elem_id, diag.diag_id)
    toolbox.set_active_module("P2")

    assert repo.diagram_read_only(diag.diag_id)
    assert repo.element_read_only(blk.elem_id)

    toolbox.rename_diagram("F1", "F2")
    rename_block(repo, blk.elem_id, "B2")
    assert repo.diagrams[diag.diag_id].name == "F1"
    assert repo.elements[blk.elem_id].name == "B1"
