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


class TableController(ttk.Treeview):
    """Unified table widget with common styling, editing and numbering.

    This controller is meant to standardize all table widgets across the
    application.  It automatically applies a common style, attaches
    scrollbars, enables in-place editing on double click and enumerates the
    visible rows.
    """

    def __init__(
        self,
        master: ttk.Widget | None = None,
        *,
        columns: tuple[str, ...] | list[str] | None = None,
        rowheight: int = 60,
        enumerate_rows: bool | None = None,
        **kwargs,
    ) -> None:
        container = kwargs.pop("container", None)
        columns = columns or kwargs.get("columns") or ()

        # Only enumerate rows when explicit columns are supplied (i.e. table
        # mode).  Tree based views that rely on the default column remain
        # untouched.
        if enumerate_rows is None:
            enumerate_rows = bool(columns)
        self._enumerate = enumerate_rows

        show = kwargs.get("show", "headings" if columns else "tree")
        if self._enumerate and "tree" not in show:
            show = f"{show} tree" if show else "tree headings"
        kwargs["show"] = show
        kwargs["columns"] = columns

        # Configure a uniform style
        style_name = kwargs.pop("style", "AutoML.Treeview")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            style_name,
            font=("Segoe UI", 10),
            rowheight=rowheight,
            borderwidth=1,
            relief="solid",
            bordercolor="black",
        )
        style.configure(
            f"{style_name}.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#d0d0d0",
            borderwidth=1,
            relief="raised",
            bordercolor="black",
        )
        kwargs["style"] = style_name

        super().__init__(master, **kwargs)

        # Set up enumeration column using the tree column text field
        if self._enumerate:
            self.heading("#0", text="#")
            self.column("#0", width=40, anchor="e", stretch=False)
            self._renumber()

        # Attach scrollbars by default
        add_treeview_scrollbars(self, container)

        # Enable basic in-place editing
        self._edit_widget: tk.Widget | None = None
        self.bind("<Double-1>", self._begin_edit, add="+")

    # ------------------------------------------------------------------
    # row enumeration helpers
    # ------------------------------------------------------------------
    def _renumber(self) -> None:
        if not self._enumerate:
            return
        for i, iid in enumerate(self.get_children(""), start=1):
            self.item(iid, text=str(i))

    def insert(self, parent: str = "", index: str | int = "end", iid=None, **kw):
        item = super().insert(parent, index, iid=iid, **kw)
        self._renumber()
        return item

    def delete(self, *items):  # type: ignore[override]
        super().delete(*items)
        self._renumber()

    # ------------------------------------------------------------------
    # basic edit support
    # ------------------------------------------------------------------
    def _begin_edit(self, event):
        if self._edit_widget:
            return
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            return
        rowid = self.identify_row(event.y)
        col = self.identify_column(event.x)
        if not rowid or not col:
            return
        if self._enumerate and col == "#0":
            return
        col_index = int(col.replace("#", "")) - 1
        col_name = self.cget("columns")[col_index]
        value = self.set(rowid, col_name)
        x, y, w, h = self.bbox(rowid, col)
        var = tk.StringVar(value=value)
        widget = tk.Entry(self, textvariable=var)
        widget.place(x=x, y=y, width=w, height=h)
        widget.focus_set()

        def save(event=None):
            self.set(rowid, col_name, var.get())
            widget.destroy()
            self._edit_widget = None

        widget.bind("<Return>", save)
        widget.bind("<FocusOut>", save)
        self._edit_widget = widget


# Replace default Treeview with the consolidated controller
_BaseTreeview = ttk.Treeview
ttk.Treeview = TableController


# ---------------------------------------------------------------------------
# Enable clickable column sorting for all ttk.Treeview tables
# ---------------------------------------------------------------------------
_orig_heading = _BaseTreeview.heading


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
