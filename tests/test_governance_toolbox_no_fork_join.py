import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import gui.architecture as arch
from gui.architecture import GovernanceDiagramWindow
from sysml.sysml_repository import SysMLRepository


def test_governance_toolbox_excludes_fork_and_join(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")

    class DummyWidget:
        def __init__(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

        def pack_forget(self, *a, **k):
            pass

        def bind(self, *a, **k):
            pass

        def configure(self, *a, **k):
            pass

        def destroy(self, *a, **k):
            pass

    def fake_sysml_init(self, master, title, tools, diagram_id=None, app=None, history=None, relation_tools=None, tool_groups=None):
        self.app = app
        self.repo = repo
        self.diagram_id = diagram_id
        self.toolbox = DummyWidget()
        self.tools_frame = DummyWidget()
        canvas_master = DummyWidget()
        self.canvas = types.SimpleNamespace(master=canvas_master)
        # Create dummy buttons for each tool
        self.tool_buttons = {name: DummyWidget() for name in tools}

    monkeypatch.setattr(arch.SysMLDiagramWindow, "__init__", fake_sysml_init)
    monkeypatch.setattr(arch, "draw_icon", lambda *a, **k: None)
    monkeypatch.setattr(arch.GovernanceDiagramWindow, "refresh_from_repository", lambda self: None)
    monkeypatch.setattr(arch.ttk, "Combobox", DummyWidget)
    monkeypatch.setattr(arch.ttk, "Frame", DummyWidget)
    monkeypatch.setattr(arch.ttk, "LabelFrame", DummyWidget)
    monkeypatch.setattr(arch.ttk, "Button", DummyWidget)

    win = GovernanceDiagramWindow(None, None, diagram_id=diag.diag_id)
    assert "Fork" not in win.tool_buttons
    assert "Join" not in win.tool_buttons
