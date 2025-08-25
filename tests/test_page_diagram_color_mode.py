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

from mainappsrc.automl_core import PageDiagram

class DummyApp:
    def __init__(self):
        self.modes = []
        self.project_properties = {}
        self.occurrence_counts = {}

    def get_node_fill_color(self, node, mode=None):
        self.modes.append(mode)
        return "#000000"


class DummyCanvas:
    diagram_mode = "CTA"

    def bind(self, *args, **kwargs):
        pass


class DummyNode:
    is_primary_instance = True
    original = None
    display_label = ""
    input_subtype = None
    description = ""
    rationale = ""
    equation = ""
    detailed_equation = ""
    name = "n"
    x = 0
    y = 0
    unique_id = 1
    node_type = "Basic Event"
    children = []
    parents = []
    is_page = False
    gate_type = "AND"


class StubDrawingHelper:
    def draw_circle_event_shape(self, *args, **kwargs):
        pass


class DummyFont:
    def config(self, *args, **kwargs):
        pass


def test_page_diagram_uses_own_mode(monkeypatch):
    from mainappsrc import AutoML as auto_module

    monkeypatch.setattr(auto_module.tkFont, "Font", lambda *a, **k: DummyFont())
    monkeypatch.setattr(auto_module, "fta_drawing_helper", StubDrawingHelper())

    app = DummyApp()
    canvas = DummyCanvas()
    pd = PageDiagram(app, DummyNode(), canvas)
    pd.draw_node(DummyNode())

    assert app.modes == ["CTA"]
