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
        diagrams={"D": "id1", "L": "id2"},
        diagrams_for_module=lambda phase: {"D"} if phase == "Phase1" else set(),
        list_modules=lambda: ["Phase1"],
        module_for_diagram=lambda name: "Phase1" if name == "D" else None,
        list_diagrams=lambda: {"D", "L"},
    )
    win.toolbox = toolbox
    win.app = types.SimpleNamespace()
    win._display_requirements = lambda *args, **kwargs: None
    monkeypatch.setattr(smt.SysMLRepository, "get_instance", lambda: object())
    return win


def test_phase_requirement_updates_existing(monkeypatch):
    win = _setup_window(monkeypatch)

    # First generation with organizational type
    monkeypatch.setattr(
        smt.GovernanceDiagram,
        "from_repository",
        lambda repo, diag_id: DummyGov([("Req", "organizational")]),
    )
    global_requirements.clear()
    win.generate_phase_requirements("Phase1")
    rids = list(global_requirements.keys())
    assert len(rids) == 1
    rid1 = rids[0]
    assert global_requirements[rid1]["phase"] == "Phase1"
    assert global_requirements[rid1]["req_type"] == "organizational"
    assert global_requirements[rid1]["status"] == "draft"

    # Regenerate with a different type; old requirement becomes obsolete and a
    # new one is created
    monkeypatch.setattr(
        smt.GovernanceDiagram,
        "from_repository",
        lambda repo, diag_id: DummyGov([("Req", "product")]),
    )
    win.generate_phase_requirements("Phase1")
    assert len(global_requirements) == 2
    assert global_requirements[rid1]["status"] == "obsolete"
    new_rid = next(r for r in global_requirements if r != rid1)
    assert global_requirements[new_rid]["req_type"] == "product"
    assert global_requirements[new_rid]["status"] == "draft"


def test_lifecycle_requirements_visible_in_phases(monkeypatch):
    win = _setup_window(monkeypatch)

    req_map = {
        "id1": [("Phase req", "organizational")],
        "id2": [("Life req", "organizational")],
    }

    def from_repo(_repo, diag_id):
        return DummyGov(req_map[diag_id])

    monkeypatch.setattr(smt.GovernanceDiagram, "from_repository", from_repo)

    captured = {}
    win._display_requirements = lambda title, ids: captured.setdefault(title, ids)

    global_requirements.clear()
    # Generate lifecycle requirement
    win.generate_lifecycle_requirements()
    life_rid = next(iter(global_requirements))
    assert global_requirements[life_rid]["phase"] is None

    # Generate phase requirements; lifecycle requirement should be included
    win.generate_phase_requirements("Phase1")
    ids = captured.get("Phase1 Requirements", [])
    assert life_rid in ids
