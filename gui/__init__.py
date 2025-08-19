# Shared GUI helpers
from __future__ import annotations

"""Shared GUI helpers and widget customizations."""

import tkinter as tk
from tkinter import ttk

from .capsule_button import CapsuleButton, _interpolate_color  # noqa: F401


class _StyledButton(CapsuleButton):
    """Base class adding optional gradient colouring support."""

    def __init__(self, *args, **kwargs):
        self._gradient = kwargs.pop("gradient", None)
        super().__init__(*args, **kwargs)

    def _draw_gradient(self, w: int, h: int) -> None:  # type: ignore[override]
        if not self._gradient:
            return
        colors = self._gradient
        stops = [i / (len(colors) - 1) for i in range(len(colors))]
        r = self._radius
        for y in range(h):
            t = y / (h - 1) if h > 1 else 0
            for i in range(len(stops) - 1):
                if stops[i] <= t <= stops[i + 1]:
                    local_t = (t - stops[i]) / (stops[i + 1] - stops[i])
                    color = _interpolate_color(colors[i], colors[i + 1], local_t)
                    break
            dy = abs(y - h / 2)
            x_offset = int(r - (r ** 2 - dy ** 2) ** 0.5) if dy <= r else 0
            self._gradient_items.append(
                self.create_line(x_offset, y, w - x_offset, y, fill=color)
            )


class TranslucidButton(_StyledButton):
    """Capsule button with a subtle translucent palette used by default."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("bg", "#ffffff")
        kwargs.setdefault("hover_bg", "#f0f0f0")
        kwargs.setdefault("gradient", ["#ffffff", "#f0f0f0"])
        super().__init__(*args, **kwargs)


class PurpleButton(_StyledButton):
    """Capsule button variant with a purplish theme for dialogs."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("bg", "#9b59b6")
        kwargs.setdefault("hover_bg", "#b37cc8")
        kwargs.setdefault("gradient", ["#9b59b6", "#8e44ad"])
        super().__init__(*args, **kwargs)


# Use ``TranslucidButton`` for all button instances across the GUI.  Monkeypatching
# both ``ttk.Button`` and the classic ``tk.Button`` ensures the custom hover
# highlight is applied consistently without modifying every call site.
ttk.Button = TranslucidButton  # type: ignore[assignment]
tk.Button = TranslucidButton  # type: ignore[assignment]

def format_name_with_phase(name: str, phase: str | None) -> str:
    """Return ``name`` with ``" (phase)"`` appended when ``phase")" is set."""

    if phase:
        return f"{name} ({phase})" if name else f"({phase})"
    return name


def add_treeview_scrollbars(tree: ttk.Treeview, container: ttk.Widget | None = None) -> None:
    """Attach both vertical and horizontal scrollbars to ``tree``.

    Parameters
    ----------
    tree:
        The ``ttk.Treeview`` widget to augment.
    container:
        Parent widget that should hold the tree and scrollbars. Defaults to
        ``tree.master``.
    """

    container = container or tree.master
    vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)


# ---------------------------------------------------------------------------
# Enable clickable column sorting for all ttk.Treeview tables
# ---------------------------------------------------------------------------
_orig_heading = ttk.Treeview.heading


def _sortable_heading(self, column, option=None, **kw):
    """Add ascending/descending sort behavior when a column header is clicked."""
    if option is None and kw and "command" not in kw:
        def sort_column(col=column):
            data = [(self.set(k, col), k) for k in self.get_children("")]

            def _is_number(val: str) -> bool:
                try:
                    float(val)
                    return True
                except Exception:
                    return False

            numeric = all(_is_number(v) for v, _ in data if v not in ("", None))
            if numeric:
                data.sort(
                    key=lambda t: float(t[0]) if t[0] not in ("", None) else float("-inf")
                )
            else:
                data.sort(key=lambda t: str(t[0]).lower())

            if not hasattr(self, "_sort_reverse"):
                self._sort_reverse = {}
            reverse = self._sort_reverse.get(col, False)
            if reverse:
                data.reverse()
            for idx, (_, item) in enumerate(data):
                self.move(item, "", idx)
            self._sort_reverse[col] = not reverse

        kw["command"] = sort_column
    return _orig_heading(self, column, option, **kw)


ttk.Treeview.heading = _sortable_heading
