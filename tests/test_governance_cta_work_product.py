import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from analysis import SafetyManagementToolbox
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def test_governance_cta_work_product_enabled(monkeypatch):
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

    enabled = []
    captured = {}

    class DummyApp:
        safety_mgmt_toolbox = toolbox

        def enable_work_product(self, name, *, refresh=True):
            enabled.append(name)

    win.app = DummyApp()

    class DummyDialog:
        def __init__(self, parent, title, options):
            if title == "Add Process Area":
                self.selection = "Safety Analysis"
            else:
                captured["wp_options"] = options
                self.selection = "CTA"

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", DummyDialog)
    win.add_work_product()

    assert "CTA" in captured.get("wp_options", [])
    assert "CTA" in enabled
    _sm.ACTIVE_TOOLBOX = prev_tb
