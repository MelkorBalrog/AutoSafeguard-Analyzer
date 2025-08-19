import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLDiagramWindow


def test_role_tooltip_connections():
    # Minimal canvas providing coordinate translation
    class DummyCanvas:
        def canvasx(self, x):
            return x
        def canvasy(self, y):
            return y

    # Dummy tooltip recording text and visibility
    class DummyTooltip:
        def __init__(self, widget, text="", automatic=False):
            self.text = text
            self.visible = False
        def show(self, x=None, y=None):
            self.visible = True
        def hide(self):
            self.visible = False

    obj = types.SimpleNamespace(obj_type="Role")
    repo = types.SimpleNamespace(diagrams={1: types.SimpleNamespace(diag_type="Governance Diagram")})
    win = types.SimpleNamespace(
        start=None,
        current_tool=None,
        canvas=DummyCanvas(),
        repo=repo,
        diagram_id=1,
        redraw=lambda: None,
        find_object=lambda x, y: obj,
        _hover_tip=DummyTooltip(None),
        _hover_obj=None,
    )

    event = types.SimpleNamespace(x=0, y=0, x_root=0, y_root=0)

    SysMLDiagramWindow.on_mouse_move(win, event)

    assert win._hover_tip.visible
    text = win._hover_tip.text
    assert "Approves: Document, Policy, Procedure, Record" in text
    assert "Uses: Data, Document, Record" in text
