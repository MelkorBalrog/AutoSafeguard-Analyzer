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

from gui import toolboxes as tb


def test_requirements_text_multiline(monkeypatch):
    created = {}

    class DummyText:
        def __init__(self, master):
            created["widget"] = "text"
            self._val = ""

        def insert(self, index, value):
            self._val = value

        def place(self, *_, **__):
            pass

        def focus_set(self):
            pass

        def bind(self, *_, **__):
            pass

        def destroy(self):
            pass

        def get(self, *_):
            return self._val

    class DummyEntry(DummyText):
        def __init__(self, master, textvariable=None):
            created["widget"] = "entry"

    class DummyCombobox(DummyEntry):
        def __init__(self, master, textvariable=None, values=None, state=None):
            super().__init__(master, textvariable)

    monkeypatch.setattr(tb.tk, "Text", DummyText)
    monkeypatch.setattr(tb.tk, "Entry", DummyEntry)
    monkeypatch.setattr(tb.ttk, "Combobox", DummyCombobox)

    tree = types.SimpleNamespace(
        _edit_widget=None,
        _multiline_cols={"Text"},
        _col_options={},
        _req_cols={},
        _req_target=None,
        _edit_cb=None,
        cget=lambda key: ("ID", "Text"),
        identify=lambda what, x, y: "cell" if what == "region" else None,
        identify_row=lambda y: "row1",
        identify_column=lambda x: "#2",
        set=lambda rowid, col_name, value=None: "old" if value is None else None,
        bbox=lambda rowid, col: (0, 0, 100, 20),
        index=lambda rowid: 0,
    )

    event = types.SimpleNamespace(x=0, y=0)
    tb.EditableTreeview._begin_edit(tree, event)

    assert created.get("widget") == "text"

