import sys
import types

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import FaultTreeApp, HazopDoc
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository


def _minimal_app():
    """Return a barebones ``FaultTreeApp`` suitable for serialisation tests."""

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.top_events = []
    app.root_node = None
    app.fmea_entries = []
    app.fmeas = []
    app.fmedas = []
    app.mechanism_libraries = []
    app.selected_mechanism_libraries = []
    app.mission_profiles = []
    app.reliability_analyses = []
    app.hazop_docs = []
    app.hara_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hazop_entries = []
    app.fi2tc_entries = []
    app.tc2fi_entries = []
    app.scenario_libraries = []
    app.odd_libraries = []
    app.faults = []
    app.malfunctions = []
    app.hazards = []
    app.failures = []
    app.project_properties = {}
    app.reviews = []
    app.review_data = types.SimpleNamespace(name=None)
    app.update_odd_elements = lambda: None
    app.update_failure_list = lambda: None
    app.load_default_mechanisms = lambda: None
    app.update_hazard_list = lambda: None
    app.update_hara_statuses = lambda: None
    app.update_fta_statuses = lambda: None
    app.get_all_basic_events = lambda: []
    app.get_all_nodes = lambda te: []
    app.get_all_fmea_entries = lambda: []
    app.update_global_requirements_from_nodes = lambda *args, **kwargs: None
    app.sync_hara_to_safety_goals = lambda: None
    app.close_page_diagram = lambda: None
    app.update_views = lambda: None
    app.safety_mgmt_toolbox = SafetyManagementToolbox()
    app.tool_listboxes = {}
    app.work_product_menus = {}
    app.tool_actions = {}
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.refresh_tool_enablement = lambda: None
    return app


def test_safety_management_roundtrip_serialisation():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()

    app = _minimal_app()
    toolbox = app.safety_mgmt_toolbox
    toolbox.create_diagram("GovA")
    toolbox.create_diagram("GovB")
    child = GovernanceModule("Child", diagrams=["GovB"])
    parent = GovernanceModule("Parent", modules=[child])
    toolbox.modules.append(parent)

    data = app.export_model_data(include_versions=False)

    new_app = _minimal_app()
    new_app.apply_model_data(data, ensure_root=False)

    new_tb = new_app.safety_mgmt_toolbox
    assert "GovA" in new_tb.diagrams
    assert new_tb.modules and new_tb.modules[0].name == "Parent"
    assert new_tb.modules[0].modules[0].diagrams == ["GovB"]


def test_apply_model_enables_governed_work_products(monkeypatch):
    app = _minimal_app()
    enabled = []
    monkeypatch.setattr(
        FaultTreeApp, "enable_work_product", lambda self, name: enabled.append(name)
    )
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(app, FaultTreeApp)
    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("Gov", "HAZOP", "Rationale")
    data = {"safety_mgmt_toolbox": toolbox.to_dict()}
    app.apply_model_data(data, ensure_root=False)
    assert enabled == ["HAZOP"]


def test_apply_model_without_governance_disables_work_products(monkeypatch):
    app = _minimal_app()
    app.enabled_work_products = {"HAZOP"}
    disabled = []
    monkeypatch.setattr(
        FaultTreeApp,
        "disable_work_product",
        lambda self, name: disabled.append(name) or True,
    )
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(app, FaultTreeApp)
    app.apply_model_data({}, ensure_root=False)
    assert disabled == ["HAZOP"]
    assert app.enabled_work_products == set()


def test_work_product_phase_roundtrip():
    app = _minimal_app()
    tb = app.safety_mgmt_toolbox
    tb.set_active_module("Phase1")
    doc = HazopDoc("HZ1", [])
    app.hazop_docs = [doc]
    tb.register_created_work_product("HAZOP", doc.name)
    data = app.export_model_data(include_versions=False)
    new_app = _minimal_app()
    new_app.apply_model_data(data, ensure_root=False)
    tb2 = new_app.safety_mgmt_toolbox
    assert tb2.doc_phases.get("HAZOP", {}).get("HZ1") == "Phase1"
    tb2.set_active_module("Phase1")
    assert tb2.document_visible("HAZOP", "HZ1")
    tb2.set_active_module("Phase2")
    assert not tb2.document_visible("HAZOP", "HZ1")


def test_enabled_work_products_roundtrip():
    app = _minimal_app()
    app.enable_work_product("HAZOP")
    data = app.export_model_data(include_versions=False)
    new_app = _minimal_app()
    new_app.apply_model_data(data, ensure_root=False)
    assert "HAZOP" in new_app.enabled_work_products

