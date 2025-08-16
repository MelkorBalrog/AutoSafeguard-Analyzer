import types

from gui.architecture import GovernanceDiagramWindow
import gui.architecture as arch


def test_governance_diagram_has_no_select_button(monkeypatch):
    class DummyButton:
        def __init__(self):
            self.config = {}

        def configure(self, **kwargs):
            self.config.update(kwargs)

        def destroy(self):
            self.destroyed = True

    def fake_sysml_init(self, master, title, tools, diagram_id=None, app=None, history=None, relation_tools=None, tool_groups=None):
        self.tool_buttons = {"Select": DummyButton(), "Action": DummyButton()}
        self.toolbox = types.SimpleNamespace()
        self.tools_frame = None
        self.rel_frame = None
        canvas_master = types.SimpleNamespace(pack_forget=lambda: None, pack=lambda **k: None)
        self.canvas = types.SimpleNamespace(master=canvas_master)
        self.repo = types.SimpleNamespace(diagrams={})
        self.diagram_id = "dummy"
        self.refresh_from_repository = lambda *_: None

    monkeypatch.setattr(arch.SysMLDiagramWindow, "__init__", fake_sysml_init)

    win = GovernanceDiagramWindow(None, None)
    assert "Select" not in win.tool_buttons
    assert "Task" in win.tool_buttons
