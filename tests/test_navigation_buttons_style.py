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

from AutoML import AutoMLApp


class DummyStyle:
    def __init__(self):
        self.configured = {}
        self.mapped = {}

    def configure(self, style, **kwargs):
        self.configured[style] = kwargs

    def map(self, style, **kwargs):
        self.mapped[style] = kwargs


def test_nav_button_style_has_active_and_pressed_background():
    app = AutoMLApp.__new__(AutoMLApp)
    app.style = DummyStyle()
    AutoMLApp._init_nav_button_style(app)
    mapping = app.style.mapped["Nav.TButton"]
    assert ("active", "#f2f6fa") in mapping.get("background", [])
    assert ("pressed", "#dae2ea") in mapping.get("background", [])

