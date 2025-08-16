import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from analysis import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
import pytest


def test_add_generic_work_product(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    from analysis import safety_management as _sm
    prev_tb = _sm.ACTIVE_TOOLBOX
    toolbox = SafetyManagementToolbox()

    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None

    enable_calls = []

    class DummyApp:
        safety_mgmt_toolbox = toolbox

        def enable_work_product(self, name, *, refresh=True):
            enable_calls.append(name)

    win.app = DummyApp()

    monkeypatch.setattr("gui.architecture.simpledialog.askstring", lambda *a, **k: "Custom WP")

    win.add_generic_work_product()

    assert enable_calls == ["Custom WP"]
    assert any(
        o.obj_type == "Work Product" and o.properties.get("name") == "Custom WP"
        for o in win.objects
    )
    assert any(wp.analysis == "Custom WP" for wp in toolbox.work_products)

    _sm.ACTIVE_TOOLBOX = prev_tb


def test_add_generic_work_product_name_conflict(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    from analysis import safety_management as _sm
    prev_tb = _sm.ACTIVE_TOOLBOX
    toolbox = SafetyManagementToolbox()

    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None

    enable_calls = []
    errors = []

    class DummyApp:
        safety_mgmt_toolbox = toolbox
        WORK_PRODUCT_INFO = {"FMEA": ("Safety Analysis", "", "")}

        def enable_work_product(self, name, *, refresh=True):
            enable_calls.append(name)

    win.app = DummyApp()

    monkeypatch.setattr("gui.architecture.simpledialog.askstring", lambda *a, **k: "FMEA")
    monkeypatch.setattr("gui.architecture.messagebox.showerror", lambda *a, **k: errors.append(a))

    win.add_generic_work_product()

    assert enable_calls == []
    assert not any(o.obj_type == "Work Product" for o in win.objects)
    assert errors

    _sm.ACTIVE_TOOLBOX = prev_tb
