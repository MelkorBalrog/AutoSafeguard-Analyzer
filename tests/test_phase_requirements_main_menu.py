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

    def fake_generate(phase):
        called.append(phase)

    app.generate_phase_requirements = fake_generate

    class DummyMenu:
        def __init__(self):
            self.items = []

        def delete(self, start, end):
            self.items.clear()

        def add_command(self, label, command):
            self.items.append((label, command))

    app.phase_req_menu = DummyMenu()

    FaultTreeApp._refresh_phase_requirements_menu(app)

    assert any(label == "Phase1" for label, _ in app.phase_req_menu.items)
    for label, cmd in app.phase_req_menu.items:
        if label == "Phase1":
            cmd()
    assert called == ["Phase1"]


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
