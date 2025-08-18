import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements


class DummyGov:
    def __init__(self, reqs):
        self._reqs = reqs

    def generate_requirements(self):
        return self._reqs


def _setup_window(monkeypatch):
    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    toolbox = types.SimpleNamespace(
        diagrams={"D": "id1"},
        diagrams_for_module=lambda phase: {"D"},
        list_modules=lambda: ["Phase1"],
        module_for_diagram=lambda name: "Phase1",
        list_diagrams=lambda: {"D"},
    )
    win.toolbox = toolbox
    win.app = types.SimpleNamespace()
    win._display_requirements = (
        lambda *args, **kwargs: types.SimpleNamespace(
            refresh_table=lambda ids: None
        )
    )
    monkeypatch.setattr(smt.SysMLRepository, "get_instance", lambda: object())
    return win


def test_existing_requirement_reused(monkeypatch):
    win = _setup_window(monkeypatch)

    monkeypatch.setattr(
        smt.GovernanceDiagram,
        "from_repository",
        lambda repo, diag_id: DummyGov([("Req1", "organizational")]),
    )
    global_requirements.clear()
    win.generate_phase_requirements("Phase1")
    assert len(global_requirements) == 1

    monkeypatch.setattr(
        smt.GovernanceDiagram,
        "from_repository",
        lambda repo, diag_id: DummyGov(
            [("Req1", "organizational"), ("Req2", "organizational")]
        ),
    )
    win.generate_phase_requirements("Phase1")
    texts = [req["text"] for req in global_requirements.values()]
    statuses = {req["text"]: req["status"] for req in global_requirements.values()}
    assert texts.count("Req1") == 1
    assert statuses["Req1"] == "draft"
    assert "Req2" in texts
    assert statuses["Req2"] == "draft"
