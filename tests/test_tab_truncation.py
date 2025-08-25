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

import types

import AutoML
from AutoML import AutoMLApp


def test_long_tab_title_truncated(monkeypatch):
    class DummyFrame:
        pass

    class DummyNotebook:
        def __init__(self):
            self._tabs = []
            self._titles = {}
            self._widgets = {}
            self.selected = None

        def tabs(self):
            return self._tabs

        def tab(self, tab_id, option):
            assert option == "text"
            return self._titles[tab_id]

        def add(self, widget, text):
            tab_id = f"id{len(self._tabs)}"
            self._tabs.append(tab_id)
            self._titles[tab_id] = text
            self._widgets[tab_id] = widget

        def select(self, tab):
            self.selected = tab

        def nametowidget(self, tab_id):
            return self._widgets[tab_id]

    monkeypatch.setattr(AutoML, "ttk", types.SimpleNamespace(Frame=lambda master: DummyFrame()))

    app = AutoMLApp.__new__(AutoMLApp)
    app.doc_nb = DummyNotebook()

    long_title = "x" * (AutoMLApp.MAX_TAB_TEXT_LENGTH + 10)
    tab = app._new_tab(long_title)

    tab_id = app.doc_nb.tabs()[0]
    displayed = app.doc_nb.tab(tab_id, "text")
    assert displayed.endswith("…")
    assert len(displayed) == AutoMLApp.MAX_TAB_TEXT_LENGTH

    second = app._new_tab(long_title)
    assert second is tab
