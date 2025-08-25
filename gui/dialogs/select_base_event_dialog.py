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
