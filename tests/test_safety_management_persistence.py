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

from AutoML import FaultTreeApp
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

