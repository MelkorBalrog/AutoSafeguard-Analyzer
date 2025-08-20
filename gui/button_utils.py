"""Utility helpers for consistent button presentation across toolboxes."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .capsule_button import _lighten


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

def _lighten_color(color: str, factor: float = 1.2) -> str:
    """Return a subtly glowing version of *color*.

    The base colour channels are scaled by *factor* and then blended with
    white and a hint of pastel green.  This mirrors the behaviour of the
    :func:`_lighten` helper used by :class:`gui.capsule_button.CapsuleButton` so
    hover images across the application share the same gentle glow.
    """

    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    r = min(int(r * factor), 255)
    g = min(int(g * factor), 255)
    b = min(int(b * factor), 255)
    # Blend with white and a touch of light green (#ccffcc)
    r = int(r * 0.6 + 255 * 0.3 + 204 * 0.1)
    g = int(g * 0.6 + 255 * 0.3 + 255 * 0.1)
    b = int(b * 0.6 + 255 * 0.3 + 204 * 0.1)
    return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"

def _lighten_image(
    img: tk.PhotoImage,
    factor: float = 1.2,
    *,
    bottom_factor: float = 1.4,
    bottom_ratio: float = 0.3,
) -> tk.PhotoImage:
    """Return a new image with all non-black pixels lightened.

    A subtle "lighting" effect is added to the lower portion of the image by
    applying a stronger lightening factor to the bottom *bottom_ratio* of
    pixels.  This creates the impression of a light source shining on the base
    of the button when hovered.
    """
    w, h = img.width(), img.height()
    new_img = tk.PhotoImage(width=w, height=h)
    highlight_start = int(h * (1 - bottom_ratio))
    for x in range(w):
        for y in range(h):
            pixel = img.get(x, y)
            # ``PhotoImage.get`` may return a tuple or an empty string for
            # transparency.  Normalise to ``#rrggbb`` when a colour is present.
            if isinstance(pixel, tuple):
                if len(pixel) == 4 and pixel[3] == 0:
                    continue
                pixel = f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
            if not pixel:
                continue
            if pixel.lower() == "#000000":
                new_img.put(pixel, (x, y))
            else:
                lf = factor * bottom_factor if y >= highlight_start else factor
                new_img.put(_lighten(pixel, lf), (x, y))
    return new_img


def add_hover_highlight(
    button: ttk.Button, image: tk.PhotoImage, factor: float = 1.2
) -> tk.PhotoImage:
    """Swap *button* image to a lighter variant on hover.

    The returned :class:`tk.PhotoImage` is the generated hover image including a
    subtle light glow toward the bottom edge.  A reference to both normal and
    hover images is stored on the button to avoid them being garbage collected.
    """

    hover_img = _lighten_image(image, factor)
    button.configure(image=image)
    # Preserve references so Tk does not discard the images
    button._normal_image = image  # type: ignore[attr-defined]
    button._hover_image = hover_img  # type: ignore[attr-defined]
    button.bind("<Enter>", lambda _e: button.configure(image=hover_img))
    button.bind("<Leave>", lambda _e: button.configure(image=image))
    return hover_img
