import os
import sys
import types


sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import FaultTreeApp
from analysis.models import global_requirements


def _minimal_app():
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.top_events = []
    app.fmeas = []
    app.fmedas = []
    app.fmea_entries = []
    app.fmeda_entries = []
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
    app.hazard_severity = {}
    app.failures = []
    app.triggering_conditions = []
    app.functional_insufficiencies = []
    app.project_properties = {}
    app.reviews = []
    app.review_data = None
    app.versions = {}
    app.update_odd_elements = lambda: None
    return app


def test_safety_concept_persistence():
    global_requirements.clear()
    app = _minimal_app()
    app.safety_concept = {
        "functional": "FSC",
        "technical": "TSC",
        "cybersecurity": "CSC",
    }
    data = app.export_model_data()
    assert data["safety_concept"]["functional"] == "FSC"
    assert data["safety_concept"]["technical"] == "TSC"
    assert data["safety_concept"]["cybersecurity"] == "CSC"

    app2 = _minimal_app()
    app2.apply_model_data(data)
    assert app2.safety_concept["functional"] == "FSC"
    assert app2.safety_concept["technical"] == "TSC"
    assert app2.safety_concept["cybersecurity"] == "CSC"

