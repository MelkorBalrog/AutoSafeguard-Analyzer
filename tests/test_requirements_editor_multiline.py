# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import gui.toolboxes as tb


class DummyTreeview:
    def __init__(self, master=None, **kwargs):
        self.columns = kwargs.get("columns", [])
        self._values = {}
        self._children = []
    def bind(self, *args, **kwargs):
        pass
    def insert(self, parent, index, values):
        iid = "0"
        for col, val in zip(self.columns, values):
            self._values[(iid, col)] = val
        self._children.append(iid)
        return iid
    def set(self, rowid, col_name, value=None):
        key = (rowid, col_name)
        if value is None:
            return self._values.get(key, "")
        self._values[key] = value
    def get_children(self):
        return list(self._children)
    def identify(self, what, x, y):
        return "cell"
    def identify_row(self, y):
        return self._children[0]
    def identify_column(self, x):
        return "#1"
    def bbox(self, rowid, col):
        return (0, 0, 100, 50)
    def index(self, rowid):
        return 0
    def cget(self, key):
        if key == "columns":
            return self.columns
        return None


class DummyEntry:
    def __init__(self, master, textvariable):
        self.textvariable = textvariable
    def place(self, **kwargs):
        pass
    def focus_set(self):
        pass
    def bind(self, *args, **kwargs):
        pass
    def destroy(self):
        pass


class DummyText:
    def __init__(self, master, wrap=None):
        self.value = ""
    def insert(self, index, value):
        self.value = value
    def get(self, start, end):
        return self.value
    def place(self, **kwargs):
        pass
    def focus_set(self):
        pass
    def bind(self, *args, **kwargs):
        pass
    def destroy(self):
        pass


class DummyStringVar:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


class DummyCombobox(DummyEntry):
    def __init__(self, master, textvariable, values=None, state=None):
        super().__init__(master, textvariable)
        self.values = values
        self.state = state


def test_multiline_edit_uses_text_widget(monkeypatch):
    monkeypatch.setattr(tb, "tk", types.SimpleNamespace(
        Entry=DummyEntry,
        Text=DummyText,
        StringVar=DummyStringVar,
    ))
    monkeypatch.setattr(tb, "ttk", types.SimpleNamespace(Combobox=DummyCombobox))
    tb.EditableTreeview.__bases__ = (DummyTreeview,)

    tree = tb.EditableTreeview(columns=("Text",), multiline_columns={"Text"})
    tree.insert("", "end", values=("hello",))

    event = types.SimpleNamespace(x=0, y=0)
    tree._begin_edit(event)

    assert isinstance(tree._edit_widget, DummyText)
