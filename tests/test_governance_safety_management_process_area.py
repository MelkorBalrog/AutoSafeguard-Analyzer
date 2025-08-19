import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from sysml.sysml_repository import SysMLRepository


def test_safety_management_process_area_available(monkeypatch):
    repo = SysMLRepository.reset_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None

    captured = {}

    class DummyDialog:
        def __init__(self, parent, title, options):
            captured["options"] = options
            self.selection = ""

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", DummyDialog)

    win.add_work_product()

    assert "Safety & Security Management" in captured["options"]
    assert len(captured["options"]) == len(set(captured["options"]))
