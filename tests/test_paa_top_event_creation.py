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
from pathlib import Path
import types

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mainappsrc.automl_core import AutoMLApp


def test_paa_diagram_has_top_event(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    class DummyCanvas:
        diagram_mode = ""

    def fake_create_tab(mode):
        app.canvas = DummyCanvas()
        app.canvas.diagram_mode = mode
        app.diagram_mode = mode

    app._create_fta_tab = fake_create_tab
    app.top_events = []
    app.cta_events = []
    app.paa_events = []
    app.update_views = lambda: None
    app.window_controllers = types.SimpleNamespace(open_page_diagram=lambda *a, **k: None)
    app.create_paa_diagram()
    assert app.canvas.diagram_mode == "PAA"
    assert app.diagram_mode == "PAA"
    assert len(app.paa_events) == 1
    assert getattr(app.paa_events[0], "is_top_event", False)
