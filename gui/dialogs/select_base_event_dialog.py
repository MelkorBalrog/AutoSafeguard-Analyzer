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

"""Dialog for selecting a base event from a list.

This dialog was previously defined within :mod:`automl_core` but has been
extracted to keep the core module compact and easier to maintain.
"""

import tkinter as tk
from tkinter import simpledialog


class SelectBaseEventDialog(simpledialog.Dialog):
    """Allow the user to choose an existing base event or create a new one."""

    def __init__(self, parent: tk.Widget, events, allow_new: bool = False):
        self.events = events
        self.allow_new = allow_new
        self.selected = None
        super().__init__(parent, title="Select Base Event")

    def body(self, master: tk.Widget):  # type: ignore[override]
        self.listbox = tk.Listbox(master, height=10, width=40)
        self._visible_events = []
        for be in self.events:
            desc = getattr(be, "description", "").strip()
            if not desc:
                continue
            self._visible_events.append(be)
            self.listbox.insert(tk.END, desc)
        if self.allow_new:
            self.listbox.insert(tk.END, "<Create New Failure Mode>")
        self.listbox.grid(row=0, column=0, padx=5, pady=5)
        return self.listbox

    def apply(self) -> None:  # type: ignore[override]
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            if self.allow_new and idx == len(self._visible_events):
                self.selected = "NEW"
            else:
                self.selected = self._visible_events[idx]


__all__ = ["SelectBaseEventDialog"]
