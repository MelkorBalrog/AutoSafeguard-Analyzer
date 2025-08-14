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
    conn = DiagramConnection(phase.obj_id, wp.obj_id, "Re-use")
    diag.connections.append(asdict(conn))

    toolbox.add_work_product("Gov", "HAZOP", "")
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("HAZOP", "Doc1")

    toolbox.set_active_module("P2")
    assert toolbox.document_visible("HAZOP", "Doc1")
    assert toolbox.document_read_only("HAZOP", "Doc1")
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
    conn = DiagramConnection(dst.obj_id, src.obj_id, "Re-use")
    diag.connections.append(asdict(conn))

    toolbox.add_work_product("Gov1", "Risk Assessment", "")
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("Risk Assessment", "RA1")

    toolbox.set_active_module("P2")
    assert toolbox.document_visible("Risk Assessment", "RA1")
    assert toolbox.document_read_only("Risk Assessment", "RA1")
    assert "Risk Assessment" in toolbox.enabled_products()


def test_activity_diagram_reuse_read_only():
    repo = _setup_repo()
    gov = repo.create_diagram("BPMN Diagram", name="Gov")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov"]), GovernanceModule(name="P2")]
    toolbox.diagrams = {"Gov": gov.diag_id}

    wp = SysMLObject(1, "Work Product", 0.0, 0.0, properties={"name": "Activity Diagram"})
    phase = SysMLObject(2, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P2"})
    gov.objects.extend([asdict(wp), asdict(phase)])
    conn = DiagramConnection(phase.obj_id, wp.obj_id, "Re-use")
    gov.connections.append(asdict(conn))

    toolbox.add_work_product("Gov", "Activity Diagram", "")
    toolbox.set_active_module("P1")
    repo.create_diagram("Activity Diagram", name="Act1")

    toolbox.set_active_module("P2")
    assert toolbox.document_visible("Activity Diagram", "Act1")
    assert toolbox.document_read_only("Activity Diagram", "Act1")


def test_phase_reuse_shows_diagrams_and_elements():
    repo = _setup_repo()
    gov = repo.create_diagram("BPMN Diagram", name="Gov")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [
        GovernanceModule(name="P1", diagrams=["Gov"]),
        GovernanceModule(name="P2"),
        GovernanceModule(name="P3"),
    ]
    toolbox.diagrams = {"Gov": gov.diag_id}

    src = SysMLObject(1, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P1"})
    dst = SysMLObject(2, "Lifecycle Phase", 0.0, 0.0, properties={"name": "P2"})
    gov.objects.extend([asdict(src), asdict(dst)])
    conn = DiagramConnection(dst.obj_id, src.obj_id, "Re-use")
    gov.connections.append(asdict(conn))

    toolbox.set_active_module("P1")
    elem = repo.create_element("Block", name="B1")
    diag = repo.create_diagram("Block Definition Diagram", name="D1")
    repo.add_element_to_diagram(diag.diag_id, elem.elem_id)

    toolbox.set_active_module("P2")
    assert elem.elem_id in repo.visible_elements()
    assert diag.diag_id in repo.visible_diagrams()

    toolbox.set_active_module("P3")
    assert elem.elem_id not in repo.visible_elements()
    assert diag.diag_id not in repo.visible_diagrams()

