from dataclasses import asdict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLObject, DiagramConnection, rename_block
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository


def _setup_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


def _prepare():
    repo = _setup_repo()
    gov = repo.create_diagram("BPMN Diagram", name="Gov")
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
    toolbox.set_active_module("P2")

    assert repo.element_read_only(blk.elem_id)

    rename_block(repo, blk.elem_id, "B2")
    assert repo.elements[blk.elem_id].name == "B1"

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
