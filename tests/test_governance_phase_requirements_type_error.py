import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from gui import safety_management_toolbox as smt
from sysml.sysml_repository import SysMLRepository
from analysis.models import global_requirements


def test_generate_phase_requirements_non_string(monkeypatch):
    repo = SysMLRepository.reset_instance()
    d1 = repo.create_diagram("Governance Diagram", name="Gov1")
    t1 = repo.create_element("Action", name="Start")
    d1.objects = [
        {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "element_id": t1.elem_id, "properties": {"name": "Start"}},
    ]

    toolbox = SafetyManagementToolbox()
    toolbox.diagrams["Gov1"] = d1.diag_id
    mod = toolbox.add_module("Phase1")
    mod.diagrams.append("Gov1")

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace(_new_tab=lambda title: None)

    displayed = []
    def display_stub(title, ids):
        displayed.append((title, ids))
        return types.SimpleNamespace(refresh_table=lambda ids: None)
    win._display_requirements = display_stub

    errors = []
    monkeypatch.setattr(smt.messagebox, "showerror", lambda t, m: errors.append((t, m)))
    infos = []
    monkeypatch.setattr(smt.messagebox, "showinfo", lambda t, m: infos.append((t, m)))

    class BadGov:
        def generate_requirements(self):
            return ["ok", ("bad",)]

    monkeypatch.setattr(smt.GovernanceDiagram, "from_repository", lambda repo, diag_id: BadGov())

    global_requirements.clear()
    win.generate_phase_requirements("Phase1")

    assert errors and any("string" in msg for _, msg in errors)
    assert infos and any("No requirements were generated" in msg for _, msg in infos)
    assert not displayed
