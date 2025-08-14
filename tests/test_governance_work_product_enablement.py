from gui.architecture import GovernanceDiagramWindow, SysMLObject
from analysis import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
import pytest


@pytest.mark.parametrize("analysis", ["FI2TC", "TC2FI"])
def test_governance_work_product_enablement(analysis, monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    from analysis import safety_management as _sm
    prev_tb = _sm.ACTIVE_TOOLBOX
    toolbox = SafetyManagementToolbox()

    # Required process area for FI2TC/TC2FI
    area = SysMLObject(1, "System Boundary", 0, 0, properties={"name": "Hazard & Threat Analysis"})

    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = [area]
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None

    enable_calls = []

    class DummyApp:
        safety_mgmt_toolbox = toolbox

        def enable_work_product(self, name, *, refresh=True):
            assert any(wp.analysis == name for wp in toolbox.work_products)
            enable_calls.append(name)

    win.app = DummyApp()

    # Pretend user selected analysis in dialog
    monkeypatch.setattr(
        GovernanceDiagramWindow,
        "_SelectDialog",
        lambda *a, **k: type("D", (), {"selection": analysis})(),
    )

    win.add_work_product()

    assert enable_calls == [analysis]
    assert any(wp.analysis == analysis for wp in toolbox.work_products)
    _sm.ACTIVE_TOOLBOX = prev_tb
