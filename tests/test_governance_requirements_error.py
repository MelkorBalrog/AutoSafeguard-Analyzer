import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
from gui import safety_management_toolbox as smt

def _raise_error(self):
    raise RuntimeError("boom")

def test_generate_requirements_error(monkeypatch):
    repo = SysMLRepository.reset_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox = SafetyManagementToolbox()
    toolbox.diagrams["Gov"] = diag.diag_id

    monkeypatch.setattr(smt.GovernanceDiagram, "generate_requirements", _raise_error)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(smt.messagebox, "showerror", lambda t, m: errors.append((t, m)))
    called: list[str] = []
    def display_stub(self, title, ids):
        called.append(title)
        return types.SimpleNamespace(refresh_table=lambda ids: None)
    monkeypatch.setattr(SafetyManagementWindow, "_display_requirements", display_stub)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace()
    win.diag_var = types.SimpleNamespace(get=lambda: "Gov")

    win.generate_requirements()

    assert errors
    assert not called

def test_generate_phase_requirements_error(monkeypatch):
    repo = SysMLRepository.reset_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    toolbox = SafetyManagementToolbox()
    toolbox.diagrams["Gov1"] = diag.diag_id
    mod = toolbox.add_module("Phase1")
    mod.diagrams.append("Gov1")

    monkeypatch.setattr(smt.GovernanceDiagram, "generate_requirements", _raise_error)
    errors: list[tuple[str, str]] = []
    monkeypatch.setattr(smt.messagebox, "showerror", lambda t, m: errors.append((t, m)))
    called: list[str] = []
    def display_stub(self, title, ids):
        called.append(title)
        return types.SimpleNamespace(refresh_table=lambda ids: None)
    monkeypatch.setattr(SafetyManagementWindow, "_display_requirements", display_stub)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace()

    win.generate_phase_requirements("Phase1")

    assert errors
    assert not called
