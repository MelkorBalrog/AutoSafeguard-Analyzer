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

import tkinter as tk

import pytest

from gui.controls.capsule_button import CapsuleButton, _darken


def test_capsule_button_darkens_when_pressed():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test", bg="#888888")
    btn.pack()
    root.update_idletasks()

    btn.event_generate("<ButtonPress-1>", x=1, y=1)
    assert btn._current_color == btn._pressed_color

    btn.event_generate("<ButtonRelease-1>", x=1, y=1)
    assert btn._current_color == btn._hover_color

    root.destroy()


def test_capsule_button_has_inner_outline():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test", bg="#888888")
    btn.pack()
    root.update_idletasks()

    expected = _darken(btn._current_color, 0.7)
    for item in btn._border_gap:
        option = "fill" if btn.type(item) == "line" else "outline"
        assert btn.itemcget(item, option) == expected

    root.destroy()
