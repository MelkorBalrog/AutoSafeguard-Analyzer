import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
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
    captured = {}

    class DummyApp:
        safety_mgmt_toolbox = toolbox

        def enable_work_product(self, name, *, refresh=True):
            enable_calls.append(name)

    win.app = DummyApp()

    class MissingWpDialog:
        def __init__(self, parent, title, options):
            captured["initial_wp_options"] = options
            self.selection = ""

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", MissingWpDialog)
    win.add_work_product()
    assert "SPI Work Document" not in captured.get("initial_wp_options", [])

    class AreaDialog:
        def __init__(self, parent, title, options):
            captured["area_options"] = options
            self.selection = "Safety & Security Management"

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", AreaDialog)
    win.add_process_area()
    assert "Safety & Security Management" in captured["area_options"]

    class WorkProductDialog:
        def __init__(self, parent, title, options):
            captured["wp_options"] = options
            self.selection = "SPI Work Document"

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", WorkProductDialog)
    win.add_work_product()

    assert "SPI Work Document" in captured["wp_options"]
    assert enable_calls == ["SPI Work Document"]
    assert any(wp.analysis == "SPI Work Document" for wp in toolbox.work_products)
    _sm.ACTIVE_TOOLBOX = prev_tb
