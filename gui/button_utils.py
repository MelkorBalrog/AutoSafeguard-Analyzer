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

def _blend_with(color: str, overlay: tuple[int, int, int], alpha: float) -> str:
    """Blend *color* towards *overlay* by *alpha*."""
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    r = int(r + (overlay[0] - r) * alpha)
    g = int(g + (overlay[1] - g) * alpha)
    b = int(b + (overlay[2] - b) * alpha)
    return f"#{r:02x}{g:02x}{b:02x}"


def _blend_with(color: str, overlay: tuple[int, int, int], alpha: float) -> str:
    """Blend *color* towards *overlay* by *alpha*."""
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    r = int(r + (overlay[0] - r) * alpha)
    g = int(g + (overlay[1] - g) * alpha)
    b = int(b + (overlay[2] - b) * alpha)
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten_image(
    img: tk.PhotoImage,
    factor: float = 1.4,
    *,
    bottom_factor: float = 1.8,
    bottom_ratio: float = 0.3,
    top_alpha: float = 0.5,
    bottom_alpha: float = 0.5,
) -> tk.PhotoImage:
    """Return a new image with all pixels lightened.

    The default factors intentionally apply a strong boost so the hover image is
    visually distinct.  The bottom portion receives both a higher lightening
    factor and a green-tinted blend, creating a pronounced glow effect.  Even
    fully black capsules are brightened so the hover state is immediately
    noticeable.
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
            lf = factor * bottom_factor if y >= highlight_start else factor
            overlay = (179, 255, 179) if y >= highlight_start else (255, 255, 255)
            alpha = bottom_alpha if y >= highlight_start else top_alpha

            if pixel.lower() == "#000000":
                # Seed black pixels with a blend first so the lightening factor
                # can meaningfully brighten them, producing a visibly lighter
                # capsule image.
                blended = _blend_with(pixel, overlay, alpha)
                light = _lighten_color(blended, lf)
            else:
                light = _lighten_color(pixel, lf)
                light = _blend_with(light, overlay, alpha)

            new_img.put(light, (x, y))
    return new_img


def add_hover_highlight(
    button: ttk.Button, image: tk.PhotoImage, factor: float = 1.4
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
