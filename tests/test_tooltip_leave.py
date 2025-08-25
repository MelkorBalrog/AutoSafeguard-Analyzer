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

from gui.tooltip import ToolTip


class DummyWidget:
    def __init__(self):
        self.bound = {}

    def bind(self, event, func):
        self.bound[event] = func

    def after_cancel(self, _id):
        pass


class DummyTipWindow:
    def __init__(self):
        self.destroyed = False

    def destroy(self):
        self.destroyed = True


def test_manual_tooltip_hides_on_leave():
    widget = DummyWidget()
    tip = ToolTip(widget, "tip", automatic=False)
    tip.tipwindow = DummyTipWindow()
    # Simulate the pointer leaving the widget
    widget.bound["<Leave>"]()
    assert tip.tipwindow is None
