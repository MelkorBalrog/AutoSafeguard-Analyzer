import types

from gui import add_listbox_hover_highlight


class DummyListbox:
    def __init__(self):
        self.bindings = {}
        self.colors = {}
        self._bg = "white"
        self._select_bg = "blue"

    def bind(self, event, func):
        self.bindings[event] = func

    def nearest(self, y):
        return int(y)

    def itemconfig(self, index, **kw):
        if "background" in kw:
            self.colors[index] = kw["background"]

    def cget(self, option):
        return self._select_bg if option == "selectbackground" else self._bg

    def curselection(self):
        return ()


def test_hover_sets_light_green_background():
    lb = DummyListbox()
    add_listbox_hover_highlight(lb)
    event = types.SimpleNamespace(y=0)
    lb.bindings["<Motion>"](event)
    assert lb.colors[0] == "#ccffcc"
    lb.bindings["<Leave>"](event)
    assert lb.colors[0] == "white"
