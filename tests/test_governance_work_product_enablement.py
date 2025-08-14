from gui.architecture import GovernanceDiagramWindow, SysMLObject
from analysis import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository


def test_add_work_product_enables_toolbox(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    toolbox = SafetyManagementToolbox()

    # Required process area for FI2TC
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

    # Pretend user selected FI2TC in dialog
    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", lambda *a, **k: type("D", (), {"selection": "FI2TC"})())

    win.add_work_product()

    assert enable_calls == ["FI2TC"]
    assert any(wp.analysis == "FI2TC" for wp in toolbox.work_products)
