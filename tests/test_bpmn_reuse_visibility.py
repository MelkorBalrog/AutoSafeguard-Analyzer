from dataclasses import asdict

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLObject, DiagramConnection
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository


def _setup_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


def test_work_product_reuse_visibility():
    repo = _setup_repo()
    diag = repo.create_diagram("BPMN Diagram", name="Gov")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov"]), GovernanceModule(name="P2")]
    toolbox.diagrams = {"Gov": diag.diag_id}

    wp = SysMLObject(1, "Work Product", 0.0, 0.0, properties={"name": "HAZOP"})
    phase = SysMLObject(2, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P2"})
    diag.objects.extend([asdict(wp), asdict(phase)])
    conn = DiagramConnection(wp.obj_id, phase.obj_id, "Re-use")
    diag.connections.append(asdict(conn))

    toolbox.add_work_product("Gov", "HAZOP", "")
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("HAZOP", "Doc1")

    toolbox.set_active_module("P2")
    assert toolbox.document_visible("HAZOP", "Doc1")
    assert "HAZOP" in toolbox.enabled_products()


def test_phase_reuse_visibility():
    repo = _setup_repo()
    diag = repo.create_diagram("BPMN Diagram", name="Gov1")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov1"]), GovernanceModule(name="P2")]
    toolbox.diagrams = {"Gov1": diag.diag_id}

    src = SysMLObject(1, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P1"})
    dst = SysMLObject(2, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P2"})
    diag.objects.extend([asdict(src), asdict(dst)])
    conn = DiagramConnection(src.obj_id, dst.obj_id, "Re-use")
    diag.connections.append(asdict(conn))

    toolbox.add_work_product("Gov1", "Risk Assessment", "")
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("Risk Assessment", "RA1")

    toolbox.set_active_module("P2")
    assert toolbox.document_visible("Risk Assessment", "RA1")
    assert "Risk Assessment" in toolbox.enabled_products()

