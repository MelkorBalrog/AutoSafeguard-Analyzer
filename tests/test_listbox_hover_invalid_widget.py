import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.button_utils import enable_listbox_hover_highlight


class DummyRoot:
    def __init__(self):
        self.bindings = {}

    def bind_class(self, cls, sequence, func, add=None):
        self.bindings[(cls, sequence)] = func


def test_listbox_highlight_ignores_non_listbox():
    root = DummyRoot()
    enable_listbox_hover_highlight(root)
    lb_on_motion = root.bindings[("Listbox", "<Motion>")]
    lb_on_leave = root.bindings[("Listbox", "<Leave>")]

    class DummyEvent:
        def __init__(self, widget):
            self.widget = widget

    lb_on_motion(DummyEvent("not a listbox"))
    lb_on_leave(DummyEvent("not a listbox"))
