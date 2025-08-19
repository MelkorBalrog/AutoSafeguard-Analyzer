# Shared GUI helpers
from __future__ import annotations

"""Shared GUI helpers and widget customizations."""

import tkinter as tk
from tkinter import ttk


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


def _create_gradient_image(width: int = 200, height: int = 200) -> tk.PhotoImage:
    """Return a vertical gradient image from light blue to white.

    The bottom few pixels use a darker grey to create a subtle 3D effect.
    """
    top = (0xAD, 0xD8, 0xE6)  # light blue
    img = tk.PhotoImage(width=width, height=height)
    for y in range(height):
        r = int(top[0] + (0xFF - top[0]) * y / (height - 1))
        g = int(top[1] + (0xFF - top[1]) * y / (height - 1))
        b = int(top[2] + (0xFF - top[2]) * y / (height - 1))
        if y > height * 0.95:
            r = g = b = 0xA0  # thin dark band at the bottom
        img.put(f"#{r:02x}{g:02x}{b:02x}", to=(0, y, width, y + 1))
    return img


def apply_gradient_theme(root: tk.Misc) -> None:
    """Apply a light-blue gradient theme to common ttk widgets."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    gradient = _create_gradient_image(400, 200)
    style.element_create("Gradient", "image", gradient, border=0, sticky="nsew")
    style.layout("TFrame", [("Gradient", {"sticky": "nsew"})])
    style.layout(
        "TButton",
        [
            (
                "Gradient",
                {
                    "sticky": "nsew",
                    "children": [
                        ("Button.focus", {"sticky": "nsew", "children": [("Button.label", {"sticky": "nsew"})]})
                    ],
                },
            )
        ],
    )
    style.configure("TButton", padding=5, relief="flat")
    # Keep a reference to prevent the image from being garbage collected
    root._gradient_image = gradient
