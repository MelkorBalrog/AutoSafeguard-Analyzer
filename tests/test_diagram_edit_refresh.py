import types
from dataclasses import asdict

from sysml.sysml_repository import SysMLRepository
from gui.architecture import SysMLDiagramWindow, SysMLObject


def test_edit_object_refreshes_diagram(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Internal Block Diagram", name="Diag")
    obj = SysMLObject(1, "Block", 0.0, 0.0)
    diag.objects.append(asdict(obj))

    win = object.__new__(SysMLDiagramWindow)
    win.app = types.SimpleNamespace(update_views=lambda: None)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = [obj]
    win.connections = []
    win.update_property_view = lambda: None
    win.redraw = lambda: None

    called = {"refresh": False}

    def fake_refresh(self, event=None):
        called["refresh"] = True

    win.refresh_from_repository = types.MethodType(fake_refresh, win)
    win._sync_to_repository = lambda: None

    monkeypatch.setattr("gui.architecture.SysMLObjectDialog", lambda *args, **kwargs: None)

    SysMLDiagramWindow._edit_object(win, obj)

    assert called["refresh"]
