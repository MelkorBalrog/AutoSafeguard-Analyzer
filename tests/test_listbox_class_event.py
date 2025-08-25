from types import SimpleNamespace
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.controls.button_utils import enable_listbox_hover_highlight, _blend_with


class DummyListbox:
    def __init__(self):
        self.items = ["a", "b"]
        self.bg = "#ffffff"
        self.configs = {}
        self._hover_index = None

    def size(self):
        return len(self.items)

    def nearest(self, y):
        return 0

    def itemconfig(self, index, **kwargs):
        self.configs[index] = kwargs

    def itemcget(self, index, option):
        return self.bg

    def cget(self, option):
        return self.bg


class DummyRoot:
    def __init__(self):
        self.bindings = {}
        self.widgets = {}

    def bind_class(self, classname, sequence, func=None, add=None):
        if func is None:
            return self.bindings[(classname, sequence)]
        self.bindings[(classname, sequence)] = func

    def nametowidget(self, name):
        return self.widgets[name]


def test_lb_on_motion_handles_widget_path():
    root = DummyRoot()
    lb = DummyListbox()
    root.widgets["lb"] = lb
    enable_listbox_hover_highlight(root)
    event = SimpleNamespace(widget="lb", y=0)
    func = root.bindings[("Listbox", "<Motion>")]
    func(event)
    assert 0 in lb.configs
    expected = _blend_with(lb.bg, (204, 255, 204), 0.5)
    assert lb.configs[0]["background"] == expected
