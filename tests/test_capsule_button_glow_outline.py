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
from gui.controls.capsule_button import CapsuleButton, _lighten


def test_glow_edges_only():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    item_types = {btn.type(i) for i in btn._glow_items}
    assert "oval" not in item_types
    root.destroy()


def test_glow_matches_button_width():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    w = int(btn["width"])
    r = btn._radius
    top_line = btn._glow_items[1]
    x1, _y1, x2, _y2 = btn.coords(top_line)
    assert x1 == r - 1
    assert x2 == w - r + 1
    root.destroy()

def test_glow_bottom_highlight():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    rects = [i for i in btn._glow_items if btn.type(i) == "rectangle"]
    assert rects, "bottom highlight not added"
    rect_id = rects[0]
    x1, y1, x2, y2 = btn.coords(rect_id)
    h = int(btn["height"])
    assert y2 == h
    assert y2 - y1 <= 3
    expected_color = _lighten(btn._normal_color, 1.6)
    assert btn.itemcget(rect_id, "fill") == expected_color
    root.destroy()
