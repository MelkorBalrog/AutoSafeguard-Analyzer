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

import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from gui.controls.mac_button_style import (
    apply_purplish_button_style,
    apply_translucid_button_style,
)
from gui import toolboxes


class DummyStyle:
    def __init__(self):
        self.configured = {}
        self.mapped = {}
        self.current_theme = None

    def configure(self, style, **kwargs):
        self.configured[style] = kwargs

    def map(self, style, **kwargs):
        self.mapped[style] = kwargs

    def theme_use(self, theme=None):
        if theme is not None:
            self.current_theme = theme
        return self.current_theme

def test_apply_purplish_button_style_configures_background():
    style = DummyStyle()
    apply_purplish_button_style(style)
    assert style.configured["Purple.TButton"]["background"] == "#9b59b6"
    assert style.current_theme == "clam"


def test_apply_translucid_button_style_sets_flat_relief():
    style = DummyStyle()
    apply_translucid_button_style(style)
    assert style.configured["TButton"]["relief"] == "flat"
    assert style.current_theme == "clam"


def test_configure_table_style_uses_translucid(monkeypatch):
    called = {}
    
    class DummyStyle:
        def theme_use(self, *a, **k):
            pass

        def configure(self, *a, **k):
            pass

        def map(self, *a, **k):
            pass

    def fake_apply(style):
        called["ok"] = isinstance(style, DummyStyle)

    monkeypatch.setattr(toolboxes.ttk, "Style", lambda: DummyStyle())
    monkeypatch.setattr(toolboxes, "apply_translucid_button_style", fake_apply)
    toolboxes.configure_table_style("TestStyle")
    assert called.get("ok")
