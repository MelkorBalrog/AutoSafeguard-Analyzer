from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox


def _obj(obj_id: int, obj_type: str, name: str) -> dict:
    return {
        "obj_id": obj_id,
        "obj_type": obj_type,
        "x": 0.0,
        "y": 0.0,
        "width": 60.0,
        "height": 80.0,
        "properties": {"name": name},
    }


def test_work_product_reuse_visible():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("BPMN Diagram", name="GovWP")
    diag.objects.extend([
        _obj(1, "Work Product", "HAZOP"),
        _obj(2, "Lifecycle Phase", "P2"),
    ])
    diag.connections.append({"src": 1, "dst": 2, "conn_type": "Re-use"})
    toolbox = SafetyManagementToolbox()
    toolbox.diagrams = {"GovWP": diag.diag_id}
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("HAZOP", "HazDoc")
    toolbox.set_active_module("P2")
    assert toolbox.document_visible("HAZOP", "HazDoc")
    assert toolbox.document_read_only("HAZOP", "HazDoc")
    toolbox.set_active_module("P3")
    assert not toolbox.document_visible("HAZOP", "HazDoc")


def test_phase_reuse_shows_all_docs():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("BPMN Diagram", name="GovPhase")
    diag.objects.extend([
        _obj(1, "Lifecycle Phase", "P1"),
        _obj(2, "Lifecycle Phase", "P2"),
    ])
    diag.connections.append({"src": 1, "dst": 2, "conn_type": "Re-use"})
    toolbox = SafetyManagementToolbox()
    toolbox.diagrams = {"GovPhase": diag.diag_id}
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("FMEA", "FmeaDoc")
    toolbox.set_active_module("P2")
    assert toolbox.document_visible("FMEA", "FmeaDoc")
    assert toolbox.document_read_only("FMEA", "FmeaDoc")
    toolbox.set_active_module("P3")
    assert not toolbox.document_visible("FMEA", "FmeaDoc")

