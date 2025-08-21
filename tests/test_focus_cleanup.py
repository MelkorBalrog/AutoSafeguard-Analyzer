import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import gui
from gui import _listbox_selection_set_v4, _treeview_selection_set_v4


class DummyListbox:
    def __init__(self):
        self.cleared = False
        self.selected = []
        self.active = None
        self.focused = False

    def selection_clear(self, start, end):
        self.cleared = True

    def selection_set(self, first, last=None):
        self.selected.append(first)

    def activate(self, index):
        self.active = index

    def focus_set(self):
        self.focused = True


class DummyTreeview:
    def __init__(self):
        self.selected = []
        self.focus_item = None

    def selection_set(self, *items):
        self.selected.extend(items)

    def focus(self, item=None):
        if item is None:
            return self.focus_item
        self.focus_item = item


def test_listbox_focus_updates():
    lb = DummyListbox()
    gui._orig_listbox_selection_set = DummyListbox.selection_set
    _listbox_selection_set_v4(lb, 0)
    _listbox_selection_set_v4(lb, 1)
    assert lb.active == 1
    assert lb.focused
    assert lb.selected == [0, 1]
    assert lb.cleared


def test_treeview_focus_updates():
    tv = DummyTreeview()
    gui._orig_treeview_selection_set = DummyTreeview.selection_set
    _treeview_selection_set_v4(tv, 'i1')
    _treeview_selection_set_v4(tv, 'i2')
    assert tv.focus() == 'i2'
