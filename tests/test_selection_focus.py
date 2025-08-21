import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.button_utils import enable_listbox_hover_highlight


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


class DummyListbox:
    def __init__(self):
        self.selection = ()
        self.active = None

    def curselection(self):
        return self.selection

    def activate(self, index):
        self.active = index

    def selection_clear(self, start, end):
        self.selection = ()

    def selection_set(self, index):
        self.selection = (index,)


class DummyTree:
    def __init__(self):
        self.sel = ()
        self.focus_item = None

    def selection(self):
        return self.sel

    def selection_set(self, item):
        if isinstance(item, (list, tuple)):
            self.sel = tuple(item)
        else:
            self.sel = (item,)

    def focus(self, item=None):
        if item is None:
            return self.focus_item
        self.focus_item = item


def test_treeview_focus_follows_selection():
    root = DummyRoot()
    tree = DummyTree()
    root.widgets["tree"] = tree
    enable_listbox_hover_highlight(root)
    tree.sel = ("b", "c")
    event = SimpleNamespace(widget="tree")
    func = root.bindings[("Treeview", "<<TreeviewSelect>>")]
    func(event)
    assert tree.focus_item == "b"
    assert tree.sel == ("b",)


def test_listbox_focus_follows_selection():
    root = DummyRoot()
    lb = DummyListbox()
    root.widgets["lb"] = lb
    enable_listbox_hover_highlight(root)
    lb.selection = (2, 3)
    event = SimpleNamespace(widget="lb")
    func = root.bindings[("Listbox", "<<ListboxSelect>>")]
    func(event)
    assert lb.active == 2
    assert lb.selection == (2,)
