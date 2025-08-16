import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("Image"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("ImageTk"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("ImageFont"))

from AutoML import FaultTreeApp
from analysis import SafetyManagementToolbox


def test_phase_requirements_menu_populated(monkeypatch):
    app = FaultTreeApp.__new__(FaultTreeApp)
    toolbox = SafetyManagementToolbox()
    toolbox.add_module("Phase1")
    app.safety_mgmt_toolbox = toolbox

    called = []

    def fake_generate_phase(phase):
        called.append(phase)

    def fake_generate_lifecycle():
        called.append("lifecycle")

    app.generate_phase_requirements = fake_generate_phase
    app.generate_lifecycle_requirements = fake_generate_lifecycle

    class DummyMenu:
        def __init__(self):
            self.items = []

        def delete(self, start, end):
            self.items.clear()

        def add_command(self, label, command):
            self.items.append((label, command))

        def add_separator(self):
            self.items.append(("-", None))


    app.phase_req_menu = DummyMenu()
    req_menu = DummyMenu()
    FaultTreeApp._add_lifecycle_requirements_menu(app, req_menu)
    FaultTreeApp._refresh_phase_requirements_menu(app)

    labels = [label for label, _ in app.phase_req_menu.items]
    assert "Phase1" in labels and "Lifecycle" in labels
    for label, cmd in app.phase_req_menu.items:
        if label == "Phase1" or label == "Lifecycle":
            cmd()
    req_labels = [label for label, _ in req_menu.items]
    assert "Lifecycle Requirements" in req_labels
    for label, cmd in req_menu.items:
        if label == "Lifecycle Requirements":
            cmd()
    assert called == ["Phase1", "lifecycle", "lifecycle"]


def test_generate_phase_requirements_delegates(monkeypatch):
    app = FaultTreeApp.__new__(FaultTreeApp)
    events = []

    def fake_open(show_diagrams=True):
        events.append(show_diagrams)

    app.open_safety_management_toolbox = fake_open
    app.safety_mgmt_window = types.SimpleNamespace(
        generate_phase_requirements=lambda p: events.append(p)
    )

    FaultTreeApp.generate_phase_requirements(app, "PhaseX")

    assert events == [False, "PhaseX"]


def test_generate_lifecycle_requirements_delegates(monkeypatch):
    app = FaultTreeApp.__new__(FaultTreeApp)
    events = []

    def fake_open(show_diagrams=True):
        events.append(show_diagrams)

    app.open_safety_management_toolbox = fake_open
    app.safety_mgmt_window = types.SimpleNamespace(
        generate_lifecycle_requirements=lambda: events.append("lifecycle")
    )

    FaultTreeApp.generate_lifecycle_requirements(app)

    assert events == [False, "lifecycle"]


def test_apply_model_data_refreshes_phase_menu(monkeypatch):
    app = FaultTreeApp.__new__(FaultTreeApp)
    # Stub required methods and attributes used during model loading
    app.disable_work_product = lambda name: None
    app.enable_work_product = lambda name: None
    app.update_failure_list = lambda: None
    app.get_all_nodes = lambda te: []
    app.get_all_fmea_entries = lambda: []
    app.get_all_basic_events = lambda: []
    app.load_default_mechanisms = lambda: None
    app.update_odd_elements = lambda: None
    app.update_global_requirements_from_nodes = lambda event: None
    app.refresh_tool_enablement = lambda: None
    app.odd_libraries = []
    app.enabled_work_products = set()
    app.project_properties = {}
    app.update_views = lambda: None

    calls: list[bool] = []
    monkeypatch.setattr(
        FaultTreeApp, "_refresh_phase_requirements_menu", lambda self: calls.append(True)
    )

    data = {"top_events": [], "safety_mgmt_toolbox": {"modules": [{"name": "P1"}]}}
    FaultTreeApp.apply_model_data(app, data, ensure_root=False)

    assert calls
    assert app.safety_mgmt_toolbox.on_change == app._on_toolbox_change
