import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from gui import safety_management_toolbox as smt
from sysml.sysml_repository import SysMLRepository
from analysis.models import global_requirements


def test_generate_phase_requirements_handles_errors(monkeypatch):
    repo = SysMLRepository.reset_instance()
    d1 = repo.create_diagram("Governance Diagram", name="Gov1")
    t1 = repo.create_element("Action", name="Start")
    t2 = repo.create_element("Action", name="Finish")
    d1.objects = [
        {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "element_id": t1.elem_id, "properties": {"name": "Start"}},
        {"obj_id": 2, "obj_type": "Action", "x": 0, "y": 0, "element_id": t2.elem_id, "properties": {"name": "Finish"}},
    ]
    d1.connections = [
        {"src": 1, "dst": 2, "conn_type": "Flow", "name": "", "properties": {}}
    ]

    toolbox = SafetyManagementToolbox()
    toolbox.diagrams["Gov1"] = d1.diag_id
    mod = toolbox.add_module("Phase1")
    mod.diagrams.append("Gov1")

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace(_new_tab=lambda title: None)

    displayed = []
    win._display_requirements = lambda title, ids: displayed.append((title, ids))

    errors = []
    monkeypatch.setattr(smt.messagebox, "showerror", lambda t, m: errors.append((t, m)))
    infos = []
    monkeypatch.setattr(smt.messagebox, "showinfo", lambda t, m: infos.append((t, m)))

    class BadGov:
        def generate_requirements(self):
            raise RuntimeError("model failed")

    monkeypatch.setattr(smt.GovernanceDiagram, "from_repository", lambda repo, diag_id: BadGov())

    global_requirements.clear()
    win.generate_phase_requirements("Phase1")

    assert errors and any("model failed" in msg for _, msg in errors)
    assert infos and any("No requirements were generated" in msg for _, msg in infos)
    assert not displayed
