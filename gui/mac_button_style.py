from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def _glow_color(color: str) -> str:
    """Return a brighter ``color`` with a subtle green tint."""

    r, g, b = _hex_to_rgb(color)
    r = int((r + 255) / 2)
    g = int((g + 255) / 2)
    b = int((b + 255) / 2)
    r = int(r * 0.9 + 204 * 0.1)
    g = int(g * 0.9 + 255 * 0.1)
    b = int(b * 0.9 + 204 * 0.1)
    return _rgb_to_hex((r, g, b))


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
        background=[("active", _glow_color("#9b59b6")), ("pressed", "#8e44ad")],
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
        background=[("active", _glow_color("#ffffff")), ("pressed", "#e0e0e0")],
        relief=[("pressed", "sunken"), ("!pressed", "flat")],
    )
    return style
