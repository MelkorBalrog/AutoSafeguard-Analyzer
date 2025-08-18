import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from gui import add_treeview_scrollbars
from gui.toolboxes import EditableTreeview, configure_table_style, _wrap_val


class TableController(tk.Frame):
    """Reusable controller for creating consistently styled tables.

    The controller wraps an :class:`EditableTreeview` widget and automatically
    attaches scrollbars, enables multi-line cell wrapping and provides a
    numbered ``#`` column for row enumeration.  The resulting ``tree`` attribute
    can be used like a normal ``ttk.Treeview`` instance.
    """

    def __init__(
        self,
        master,
        *,
        columns: tuple[str, ...],
        headers: dict[str, str] | None = None,
        style_name: str = "App.Treeview",
        column_widths: dict[str, int] | None = None,
        wraplengths: dict[str, int] | None = None,
        rowheight: int = 40,
        **tree_kwargs,
    ) -> None:
        super().__init__(master)
        headers = headers or {c: c.title() for c in columns}
        column_widths = column_widths or {}
        self._wrap = wraplengths or {}
        self._base_rowheight = rowheight
        configure_table_style(style_name, rowheight=rowheight)
        self.tree = EditableTreeview(
            self,
            columns=("index",) + tuple(columns),
            show="headings",
            style=style_name,
            **tree_kwargs,
        )
        self.tree.heading("index", text="#")
        self.tree.column("index", width=40, anchor="center", stretch=False)
        for col in columns:
            self.tree.heading(col, text=headers.get(col, col.title()))
            width = column_widths.get(col, 120)
            self.tree.column(col, width=width, stretch=True)
        add_treeview_scrollbars(self.tree, self)
        self.tree.bind("<Configure>", self._adjust_text, add="+")

    # ------------------------------------------------------------------
    def clear(self) -> None:
        """Remove all rows from the table."""
        self.tree.delete(*self.tree.get_children())

    # ------------------------------------------------------------------
    def insert_row(self, values: tuple[str, ...], tags: tuple[str, ...] = ()) -> None:
        """Insert a row and update enumeration."""
        idx = len(self.tree.get_children()) + 1
        wrapped = []
        for col, val in zip(self.tree.cget("columns")[1:], values):
            wrap = self._wrap.get(col, 40)
            wrapped.append(_wrap_val(val, wrap))
        self.tree.insert("", "end", values=(idx, *wrapped), tags=tags)

    # ------------------------------------------------------------------
    def _adjust_text(self, event=None) -> None:
        """Re-wrap cell text based on current column widths."""
        try:
            font = tkfont.nametofont("TkDefaultFont")
        except Exception:
            return
        char_w = font.measure("0") or 1
        max_lines = 1
        for col in self.tree.cget("columns")[1:]:
            width = self.tree.column(col, width=None)
            if width <= 0:
                continue
            wrap = max(int(width / char_w), 1)
            for item in self.tree.get_children():
                raw = self.tree.set(item, col).replace("\n", " ")
                wrapped = _wrap_val(raw, wrap)
                self.tree.set(item, col, wrapped)
                lines = wrapped.count("\n") + 1
                if lines > max_lines:
                    max_lines = lines
        style = ttk.Style()
        line_h = font.metrics("linespace")
        style.configure(self.tree.cget("style"), rowheight=max(line_h * max_lines, self._base_rowheight))
        for idx, item in enumerate(self.tree.get_children(), start=1):
            self.tree.set(item, "index", idx)

    # ------------------------------------------------------------------
    def adjust_text(self) -> None:
        """Public wrapper for :meth:`_adjust_text`."""
        self._adjust_text()
