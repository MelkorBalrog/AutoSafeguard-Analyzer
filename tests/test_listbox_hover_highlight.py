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
import tkinter as tk
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.controls.button_utils import enable_listbox_hover_highlight


def _rgb(value):
    if isinstance(value, tuple):
        return value[:3]
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def test_listbox_row_highlight_on_hover():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")

    enable_listbox_hover_highlight(root)
    lb = tk.Listbox(root)
    lb.insert("end", "a", "b")
    lb.pack()
    root.update_idletasks()

    orig = lb.itemcget(0, "background")
    x, y, w, h = lb.bbox(0)
    lb.event_generate("<Motion>", x=x + 1, y=y + 1)
    root.update_idletasks()
    hover = lb.itemcget(0, "background")
    assert hover != orig
    r, g, b = _rgb(hover)
    assert g - max(r, b) >= 20

    x2, y2, w2, h2 = lb.bbox(1)
    lb.event_generate("<Motion>", x=x2 + 1, y=y2 + 1)
    root.update_idletasks()
    assert lb.itemcget(0, "background") == orig
    root.destroy()
