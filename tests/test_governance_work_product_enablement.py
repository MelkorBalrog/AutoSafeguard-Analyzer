import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from analysis import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
import pytest


@pytest.mark.parametrize(
    "analysis, area_name",
    [
        ("FI2TC", "Hazard & Threat Analysis"),
        ("TC2FI", "Hazard & Threat Analysis"),
        ("Scenario Library", "Scenario"),
        ("ODD", "Scenario"),
        ("Mission Profile", "Safety Analysis"),
        ("Reliability Analysis", "Safety Analysis"),
        ("Risk Assessment", "Risk Assessment"),
    ],
)
def test_governance_work_product_enablement(analysis, area_name, monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    from analysis import safety_management as _sm
    prev_tb = _sm.ACTIVE_TOOLBOX
    toolbox = SafetyManagementToolbox()

    # Required process area for the selected work product
    area = SysMLObject(1, "System Boundary", 0, 0, properties={"name": area_name})

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
    captured = {}

    class DummyApp:
        safety_mgmt_toolbox = toolbox

        def enable_work_product(self, name, *, refresh=True):
            assert any(wp.analysis == name for wp in toolbox.work_products)
            enable_calls.append(name)

    win.app = DummyApp()

    class DummyDialog:
        def __init__(self, parent, title, options):
            captured["options"] = options
            self.selection = analysis

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", DummyDialog)

    win.add_work_product()

    assert analysis in captured["options"]
    assert enable_calls == [analysis]
    assert any(wp.analysis == analysis for wp in toolbox.work_products)
    _sm.ACTIVE_TOOLBOX = prev_tb
