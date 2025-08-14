import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository


def _setup():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag_id = toolbox.create_diagram("Gov1")
    toolbox.modules = [GovernanceModule("P1", diagrams=["Gov1"])]
    toolbox.diagrams["Gov1"] = diag_id
    toolbox.add_work_product("Gov1", "FMEA", "")
    toolbox.add_work_product("Gov1", "FTA", "")
    return repo, toolbox, diag_id


def test_freeze_after_work_product_blocks_changes():
    repo, toolbox, diag_id = _setup()
    toolbox.set_active_module("P1")
    toolbox.register_created_work_product("FMEA", "Doc1")
    mod = toolbox._find_module("P1", toolbox.modules)
    assert mod.frozen
    assert repo.diagrams[diag_id].locked
    toolbox.rename_module("P1", "P1_new")
    assert toolbox.modules[0].name == "P1"
    toolbox.add_work_product("Gov1", "FMEDA", "")
    assert all(wp.analysis != "FMEDA" for wp in toolbox.work_products)
    assert not toolbox.remove_work_product("Gov1", "FTA")
    toolbox.rename_diagram("Gov1", "GovX")
    assert repo.diagrams[diag_id].name == "Gov1"


def test_freeze_on_element_creation_blocks_changes():
    repo, toolbox, diag_id = _setup()
    toolbox.set_active_module("P1")
    repo.create_element("Block", "B1")
    mod = toolbox._find_module("P1", toolbox.modules)
    assert mod.frozen
    toolbox.rename_module("P1", "P1_new")
    assert toolbox.modules[0].name == "P1"
    toolbox.add_work_product("Gov1", "FMEDA", "")
    assert all(wp.analysis != "FMEDA" for wp in toolbox.work_products)
    assert not toolbox.remove_work_product("Gov1", "FTA")
    toolbox.rename_diagram("Gov1", "GovX")
    assert repo.diagrams[diag_id].name == "Gov1"
