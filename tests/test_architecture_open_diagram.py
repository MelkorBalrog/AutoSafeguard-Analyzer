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
