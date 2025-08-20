# Shared GUI helpers
from __future__ import annotations

"""Shared GUI helpers and widget customizations."""

import tkinter as tk
from tkinter import ttk, simpledialog

from .capsule_button import CapsuleButton, _interpolate_color, _glow_color  # noqa: F401


LIGHT_BLUE = "#A9BCE2"

# ---------------------------------------------------------------------------
# Apply a consistent light blue background to all dialog windows
# ---------------------------------------------------------------------------

_orig_toplevel_init = tk.Toplevel.__init__


def _themed_toplevel_init(self, *args, **kwargs):
    _orig_toplevel_init(self, *args, **kwargs)
    try:
        self.configure(bg=LIGHT_BLUE)
    except tk.TclError:
        pass


tk.Toplevel.__init__ = _themed_toplevel_init  # type: ignore[assignment]


def _apply_bg(widget: tk.Misc) -> None:
    """Recursively apply the dialog background colour to ``widget``."""

    try:
        widget.configure(bg=LIGHT_BLUE)
    except Exception:
        pass
    for child in widget.winfo_children():
        _apply_bg(child)


_orig_dialog_init = simpledialog.Dialog.__init__


def _themed_dialog_init(self, parent, title=None):  # type: ignore[override]
    _orig_dialog_init(self, parent, title)
    _apply_bg(self)


simpledialog.Dialog.__init__ = _themed_dialog_init  # type: ignore[assignment]


class _StyledButton(CapsuleButton):
    """Base class adding optional gradient colouring support."""

    def __init__(self, *args, **kwargs):
        gradient = kwargs.pop("gradient", None)
        hover_gradient = kwargs.pop("hover_gradient", None)
        super().__init__(*args, gradient=gradient, hover_gradient=hover_gradient, **kwargs)


class TranslucidButton(_StyledButton):
    """Capsule button with a subtle translucent palette."""

    def __init__(self, *args, **kwargs):
        bg = kwargs.setdefault("bg", "#ffffff")
        gradient = kwargs.setdefault("gradient", ["#ffffff", "#f7f7f7", "#ececec"])
        kwargs.setdefault("hover_bg", _glow_color(bg))
        kwargs.setdefault("hover_gradient", [_glow_color(c) for c in gradient])
        super().__init__(*args, **kwargs)


class PurpleButton(_StyledButton):
    """Capsule button variant with a translucent purple theme for dialogs."""

    def __init__(self, *args, **kwargs):
        bg = kwargs.setdefault("bg", "#f3eaff")
        gradient = kwargs.setdefault("gradient", ["#f8f6ff", "#e7ddff", "#d9c2ff", "#f3eaff"])
        kwargs.setdefault("hover_bg", _glow_color(bg))
        kwargs.setdefault("hover_gradient", [_glow_color(c) for c in gradient])
        super().__init__(*args, **kwargs)


# Use ``CapsuleButton`` for all standard button instances across the GUI.  Toolbox
# buttons explicitly use ``TranslucidButton`` for a lighter appearance.
ttk.Button = CapsuleButton  # type: ignore[assignment]
tk.Button = CapsuleButton  # type: ignore[assignment]


def add_listbox_hover_highlight(lb: tk.Listbox) -> None:
    """Highlight listbox rows on mouse hover.

    The hovered item receives a light green background, reverting to the
    widget's original ``bg`` (or ``selectbackground`` when selected) when the
    pointer leaves.  This provides a subtle square shading from white to light
    green, helping users track list items under the cursor.
    """

    default_bg = lb.cget("bg")

    def _restore(index: int | None) -> None:
        if index is None:
            return
        bg = default_bg
        if index in lb.curselection():
            bg = lb.cget("selectbackground")
        try:
            lb.itemconfig(index, background=bg)
        except Exception:  # pragma: no cover - defensive for non-Tk dummies
            pass

    def _on_motion(event: object) -> None:
        index = lb.nearest(getattr(event, "y", 0))
        prev = getattr(lb, "_hover_index", None)
        if prev != index:
            _restore(prev)
            try:
                lb.itemconfig(index, background="#ccffcc")
            except Exception:  # pragma: no cover
                pass
            lb._hover_index = index  # type: ignore[attr-defined]

    def _on_leave(_event: object) -> None:
        _restore(getattr(lb, "_hover_index", None))
        lb._hover_index = None  # type: ignore[attr-defined]

    lb.bind("<Motion>", _on_motion)
    lb.bind("<Leave>", _on_leave)


class HoverListbox(tk.Listbox):
    """Listbox variant that applies hover highlighting automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_listbox_hover_highlight(self)


tk.Listbox = HoverListbox  # type: ignore[assignment]

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
