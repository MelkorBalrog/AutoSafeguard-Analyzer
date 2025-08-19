"""Utility helpers for consistent button presentation across toolboxes."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def set_uniform_button_width(widget: tk.Misc) -> None:
    """Ensure all ``ttk.Button`` children of *widget* share the same width.

    The width is based on the longest button label to avoid truncation and
    provide a consistent appearance across diagram toolboxes.
    """
    widget.update_idletasks()
    buttons: list[ttk.Button] = []
    max_chars = 0

    def _collect(w: tk.Misc) -> None:
        nonlocal max_chars
        for child in w.winfo_children():
            if isinstance(child, ttk.Button):
                buttons.append(child)
                try:
                    text = str(child.cget("text"))
                except tk.TclError:
                    text = str(getattr(child, "_text", ""))
                max_chars = max(max_chars, len(text))
            else:
                _collect(child)

    _collect(widget)
    if not buttons:
        return

    max_chars += 2  # Account for padding inside the button
    for btn in buttons:
        btn.configure(width=max_chars)
