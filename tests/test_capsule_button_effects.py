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
from gui.controls.capsule_button import CapsuleButton


def test_text_without_shadow_or_highlight():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test")
    btn.pack()
    root.update_idletasks()
    assert not hasattr(btn, "_text_shadow_item")
    assert not hasattr(btn, "_text_highlight_item")
    root.destroy()


def test_icon_without_highlight_or_shadow():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    img = tk.PhotoImage(width=10, height=10)
    btn = CapsuleButton(root, image=img)
    btn.pack()
    root.update_idletasks()
    assert getattr(btn, "_icon_highlight_item", None) is not None
    assert not hasattr(btn, "_icon_shadow_item")
    root.destroy()


def test_glow_on_hover_and_press():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    assert btn._glow_items == []
    btn._on_enter(type("E", (), {})())
    assert btn._glow_items
    btn._on_press(type("E", (), {})())
    assert btn._glow_items == []
    btn._on_release(type("E", (), {"x":1,"y":1})())
    assert btn._glow_items
    root.destroy()


def test_glow_outline_matches_button_size():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow", width=120, height=40)
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    w, h = int(btn["width"]), int(btn["height"])
    bbox = btn.bbox(*btn._glow_items)
    assert bbox == (0, 0, w, h)
    root.destroy()
