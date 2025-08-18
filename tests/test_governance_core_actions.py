import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow
from gui import architecture


def test_governance_core_has_add_buttons(monkeypatch):
    class DummyFrame:
        def __init__(self, master=None, text=None):
            self.master = master
            self.text = text
            self.children = []
            if master and hasattr(master, "children"):
                master.children.append(self)

        def pack(self, *args, **kwargs):
            pass

        def pack_forget(self, *args, **kwargs):
            pass

        def destroy(self, *args, **kwargs):
            pass

    class DummyButton:
        def __init__(self, master=None, text="", image=None, compound=None, command=None):
            self.master = master
            self.text = text
            self.command = command
            if master and hasattr(master, "children"):
                master.children.append(self)

        def pack(self, *args, **kwargs):
            pass

        def configure(self, **kwargs):
            self.text = kwargs.get("text", self.text)

        def destroy(self):
            pass

    monkeypatch.setattr(architecture.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(architecture.ttk, "LabelFrame", DummyFrame)
    monkeypatch.setattr(architecture.ttk, "Button", DummyButton)

    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    toolbox = DummyFrame()
    toolbox.tk = True
    win.toolbox = toolbox
    win.tools_frame = DummyFrame(toolbox)
    win.rel_frame = DummyFrame(toolbox)
    win._icon_for = lambda name: None
    win.toolbox_selector = types.SimpleNamespace(configure=lambda **k: None)
    win.toolbox_var = types.SimpleNamespace(get=lambda: "Governance", set=lambda v: None)
    win._toolbox_frames = {}

    win._rebuild_toolboxes()
    assert "Governance" in win._toolbox_frames
    assert "Governance Core" not in win._toolbox_frames
    core_frames = win._toolbox_frames["Governance"]
    actions = core_frames[1]
    labels = [child.text for child in getattr(actions, "children", [])]
    assert {
        "Add Work Product",
        "Add Generic Work Product",
        "Add Process Area",
        "Add Lifecycle Phase",
    } <= set(labels)
