"""Utility helpers for consistent button presentation across toolboxes."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def set_uniform_button_width(widget: tk.Misc) -> None:
    """Ensure all ``ttk.Button`` children of *widget* share the same width.

    ``CapsuleButton`` derivatives like ``TranslucidButton`` express width in
    *pixels* rather than character units.  Simply matching on label length can
    therefore yield inconsistent button sizes or truncated text.  By measuring
    each button's requested pixel width we can apply a uniform size that fits
    all labels.
    """
    widget.update_idletasks()
    buttons: list[ttk.Button] = []

    def _collect(w: tk.Misc) -> None:
        for child in w.winfo_children():
            if isinstance(child, ttk.Button):
                buttons.append(child)
            else:
                _collect(child)

    _collect(widget)
    if not buttons:
        return

    max_width = max(btn.winfo_reqwidth() for btn in buttons)
    for btn in buttons:
        try:
            btn.configure(width=max_width)
        except Exception:  # pragma: no cover - defensive
            pass
