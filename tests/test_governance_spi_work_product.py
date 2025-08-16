import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from analysis import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository


def test_governance_spi_work_product_enablement(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    from analysis import safety_management as _sm
    prev_tb = _sm.ACTIVE_TOOLBOX
    toolbox = SafetyManagementToolbox()

    area = SysMLObject(1, "System Boundary", 0, 0, properties={"name": "Safety Analysis"})

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
            enable_calls.append(name)

    win.app = DummyApp()

    class DummyDialog:
        def __init__(self, parent, title, options):
            captured["options"] = options
            self.selection = "SPI"

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", DummyDialog)

    win.add_work_product()

    assert "SPI" in captured["options"]
    assert enable_calls == ["SPI"]
    assert any(wp.analysis == "SPI" for wp in toolbox.work_products)
    _sm.ACTIVE_TOOLBOX = prev_tb
