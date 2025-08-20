import types

from gui.architecture import ArchitectureManagerDialog
from sysml.sysml_repository import SysMLRepository


def test_open_diagram_uses_diag_id():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Use Case Diagram", name="UC")

    called = []

    def fake_open_arch_window(arg):
        called.append(arg)

    app = types.SimpleNamespace(open_arch_window=fake_open_arch_window, diagram_tabs={})

    explorer = ArchitectureManagerDialog.__new__(ArchitectureManagerDialog)
    explorer.repo = repo
    explorer.app = app
    explorer.master = None

    explorer.open_diagram(diag.diag_id)

    assert called == [diag.diag_id]


def test_open_diagram_returns_window(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Use Case Diagram", name="UC")

    class StubWindow:
        def winfo_children(self):
            return []

    class FakeTab:
        def __init__(self, child):
            self.child = child

        def winfo_exists(self):
            return True

        def winfo_children(self):
            return [self.child]

    app = types.SimpleNamespace(diagram_tabs={}, open_arch_window=lambda d: app.diagram_tabs.update({d: FakeTab(StubWindow())}))

    explorer = ArchitectureManagerDialog.__new__(ArchitectureManagerDialog)
    explorer.repo = repo
    explorer.app = app
    explorer.master = None

    monkeypatch.setattr("gui.architecture.SysMLDiagramWindow", StubWindow)

    win = explorer.open_diagram(diag.diag_id)
    assert isinstance(win, StubWindow)
