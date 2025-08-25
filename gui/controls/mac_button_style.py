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


from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, ttk


def apply_mac_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Configure ``ttk.Button`` widgets to mimic macOS capsule buttons.

    The function adjusts padding, border and relief to give buttons a rounded
    3D appearance that resembles native macOS controls.  The style changes are
    applied to the passed ``ttk.Style`` instance.  If no *style* is supplied a
    new instance is created.
    """
    style = style or ttk.Style()
    style.configure(
        "TButton",
        padding=(10, 5),
        relief="raised",
        borderwidth=1,
        foreground="black",
        background="#e1e1e1",
    )
    style.map(
        "TButton",
        background=[("active", "#f5f5f5"), ("pressed", "#d9d9d9")],
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
    )
    return style


def apply_purplish_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Style buttons with a purple theme for message boxes."""

    style = style or ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "Purple.TButton",
        padding=(10, 5),
        relief="raised",
        borderwidth=1,
        foreground="white",
        background="#9b59b6",
    )
    style.map(
        "Purple.TButton",
        background=[("active", "#b37cc8"), ("pressed", "#8e44ad")],
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
    )
    return style


def apply_translucid_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Style the default ``ttk.Button`` with a subtle, translucent look."""

    style = style or ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "TButton",
        padding=(10, 5),
        relief="flat",
        borderwidth=1,
        foreground="black",
        background="#ffffff",
    )
    style.map(
        "TButton",
        background=[("active", "#f0f0f0"), ("pressed", "#e0e0e0")],
        relief=[("pressed", "sunken"), ("!pressed", "flat")],
    )
    return style


def _purplish_buttonbox(self) -> None:
    """Default ``simpledialog`` button box with purple-themed buttons."""

    box = ttk.Frame(self)
    apply_purplish_button_style()
    ttk.Button(
        box,
        text="OK",
        width=10,
        command=self.ok,
        style="Purple.TButton",
    ).pack(side=tk.LEFT, padx=5, pady=5)
    ttk.Button(
        box,
        text="Cancel",
        width=10,
        command=self.cancel,
        style="Purple.TButton",
    ).pack(side=tk.LEFT, padx=5, pady=5)
    self.bind("<Return>", self.ok)
    self.bind("<Escape>", self.cancel)
    box.pack()


def enable_purplish_dialog_buttons() -> None:
    """Monkeypatch ``simpledialog.Dialog`` to use purple buttons everywhere."""

    simpledialog.Dialog.buttonbox = _purplish_buttonbox


enable_purplish_dialog_buttons()
