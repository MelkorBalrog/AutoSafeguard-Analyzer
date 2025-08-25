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

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.controls.button_utils import enable_listbox_hover_highlight


class DummyRoot:
    def __init__(self):
        self.bindings = {}

    def bind_class(self, cls, sequence, func, add=None):
        self.bindings[(cls, sequence)] = func


def test_listbox_highlight_ignores_non_listbox():
    root = DummyRoot()
    enable_listbox_hover_highlight(root)
    lb_on_motion = root.bindings[("Listbox", "<Motion>")]
    lb_on_leave = root.bindings[("Listbox", "<Leave>")]

    class DummyEvent:
        def __init__(self, widget):
            self.widget = widget

    lb_on_motion(DummyEvent("not a listbox"))
    lb_on_leave(DummyEvent("not a listbox"))
