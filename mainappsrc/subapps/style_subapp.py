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

"""UI styling helper used by :class:`AutoMLApp`.

The :class:`StyleSubApp` class isolates the verbose ttk style configuration
from the main application class so that :mod:`AutoML` acts primarily as a thin
orchestration layer.
"""

import tkinter as tk
from tkinter import ttk


class StyleSubApp:
    """Configure ttk styles for the application."""

    def __init__(self, root: tk.Misc, style: ttk.Style) -> None:
        self.root = root
        self.style = style
        self.btn_images: dict[str, tk.PhotoImage] = {}

    def apply(self) -> None:
        """Apply the style configuration."""

        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure(
            "Treeview",
            font=("Arial", 10),
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="black",
            borderwidth=1,
            relief="sunken",
        )
        self.style.configure(
            "Treeview.Heading",
            background="#b5bdc9",
            foreground="black",
            relief="raised",
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", "#4a6ea9"), ("!active", "#b5bdc9")],
            foreground=[("active", "white"), ("!active", "black")],
        )
        # ------------------------------------------------------------------
        # Global color theme inspired by Windows classic / Windows 7
        # ------------------------------------------------------------------
        # Overall workspace background
        self.root.configure(background="#f0f0f0")
        # General widget colours
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", foreground="black")
        self.style.configure(
            "TEntry", fieldbackground="#ffffff", background="#ffffff", foreground="black"
        )
        self.style.configure(
            "TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            foreground="black",
        )
        self.style.configure(
            "TMenubutton", background="#e7edf5", foreground="black"
        )
        self.style.configure(
            "TScrollbar",
            background="#c0d4eb",
            troughcolor="#e2e6eb",
            bordercolor="#888888",
            arrowcolor="#555555",
            lightcolor="#eaf2fb",
            darkcolor="#5a6d84",
            borderwidth=2,
            relief="raised",
        )
        # Apply the scrollbar styling to both orientations
        for orient in ("Horizontal.TScrollbar", "Vertical.TScrollbar"):
            self.style.configure(
                orient,
                background="#c0d4eb",
                troughcolor="#e2e6eb",
                bordercolor="#888888",
                arrowcolor="#555555",
                lightcolor="#eaf2fb",
                darkcolor="#5a6d84",
                borderwidth=2,
                relief="raised",
            )
        # Toolbox/LabelFrame titles
        self.style.configure(
            "Toolbox.TLabelframe",
            background="#fef9e7",
            bordercolor="#888888",
            lightcolor="#fffef7",
            darkcolor="#bfae6a",
            borderwidth=1,
            relief="raised",
        )
        self.style.configure(
            "Toolbox.TLabelframe.Label",
            background="#fef9e7",
            foreground="black",
            font=("Segoe UI", 10, "bold"),
            padding=(4, 0, 0, 0),
            anchor="w",
        )
        # Notebook (ribbon-like) title bars with beveled edges
        self.style.configure(
            "TNotebook",
            background="#c0d4eb",
            lightcolor="#eaf2fb",
            darkcolor="#5a6d84",
            borderwidth=2,
            relief="raised",
        )
        self.style.configure(
            "TNotebook.Tab",
            background="#b5bdc9",
            foreground="#555555",
            borderwidth=1,
            relief="raised",
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#4a6ea9"), ("!selected", "#b5bdc9")],
            foreground=[("selected", "white"), ("!selected", "#555555")],
        )
        # Closable notebook shares the same appearance
        self.style.configure(
            "ClosableNotebook",
            background="#c0d4eb",
            lightcolor="#eaf2fb",
            darkcolor="#5a6d84",
            borderwidth=2,
            relief="raised",
        )
        self.style.configure(
            "ClosableNotebook.Tab",
            background="#b5bdc9",
            foreground="#555555",
            borderwidth=1,
            relief="raised",
        )
        self.style.map(
            "ClosableNotebook.Tab",
            background=[("selected", "#4a6ea9"), ("!selected", "#b5bdc9")],
            foreground=[("selected", "white"), ("!selected", "#555555")],
        )
        # Mac-like capsule buttons
        def _build_pill(top: str, bottom: str) -> tk.PhotoImage:
            img = tk.PhotoImage(width=40, height=20)
            img.put("#000000", to=(0, 0, 40, 20))
            try:
                img.transparency_set(0, 0, 0)
            except Exception:
                pass
            radius = 10
            t_r = int(top[1:3], 16)
            t_g = int(top[3:5], 16)
            t_b = int(top[5:7], 16)
            b_r = int(bottom[1:3], 16)
            b_g = int(bottom[3:5], 16)
            b_b = int(bottom[5:7], 16)
            for y in range(20):
                ratio = y / 19
                r = int(t_r * (1 - ratio) + b_r * ratio)
                g = int(t_g * (1 - ratio) + b_g * ratio)
                b = int(t_b * (1 - ratio) + b_b * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                for x in range(40):
                    if x < radius:
                        if (x - radius) ** 2 + (y - radius) ** 2 <= radius ** 2:
                            img.put(color, (x, y))
                    elif x >= 40 - radius:
                        if (x - (40 - radius - 1)) ** 2 + (y - radius) ** 2 <= radius ** 2:
                            img.put(color, (x, y))
                    else:
                        img.put(color, (x, y))
            return img

        self.btn_images = {
            "normal": _build_pill("#fdfdfd", "#d2d2d2"),
            "active": _build_pill("#eaeaea", "#c8c8c8"),
            "pressed": _build_pill("#d0d0d0", "#a5a5a5"),
        }
        # Avoid creating the element more than once to prevent TclError
        if "RoundedButton" not in self.style.element_names():
            self.style.element_create(
                "RoundedButton",
                "image",
                self.btn_images["normal"],
                ("active", self.btn_images["active"]),
                ("pressed", self.btn_images["pressed"]),
                border=10,
                sticky="nsew",
            )
        self.style.map(
            "TButton",
            relief=[("pressed", "sunken"), ("!pressed", "raised")],
        )
        # Increase notebook tab font/size so titles are fully visible
        self.style.configure(
            "TNotebook.Tab", font=("Arial", 10), padding=(10, 5), width=20
        )
        self.style.configure(
            "ClosableNotebook.Tab", font=("Arial", 10), padding=(10, 5), width=20
        )
