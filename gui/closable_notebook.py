"""Custom ttk.Notebook widget with close buttons on the left of each tab."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ClosableNotebook(ttk.Notebook):
    """Notebook widget with an 'x' button on the left side of each tab."""

    def __init__(self, master: tk.Widget | None = None, **kw):
        self._close_img = self._create_close_image()
        style = ttk.Style()
        style.element_create(
            "close",
            "image",
            self._close_img,
            border=8,
            sticky="",
        )
        style.layout(
            "ClosableNotebook.Tab",
            [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Notebook.focus",
                                            {
                                                "side": "top",
                                                "sticky": "nswe",
                                                "children": [
                                                    ("close", {"side": "left", "sticky": ""}),
                                                    ("Notebook.label", {"side": "left", "sticky": ""}),
                                                ],
                                            },
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.layout("ClosableNotebook", style.layout("TNotebook"))
        kw["style"] = "ClosableNotebook"
        super().__init__(master, **kw)
        self._active: int | None = None
        self._closing_tab: str | None = None
        self.protected: set[str] = set()
        self._drag_tab: int | None = None
        self._dragging = False
        self.bind("<ButtonPress-1>", self._on_close_press, True)
        # Allow other handlers to process releases as well
        self.bind("<ButtonRelease-1>", self._on_close_release, True)
        # Bindings for drag/detach support
        self.bind("<ButtonPress-1>", self._on_tab_press, True)
        self.bind("<B1-Motion>", self._on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self._on_tab_release, True)

    def _create_close_image(self, size: int = 10) -> tk.PhotoImage:
        img = tk.PhotoImage(width=size, height=size)
        img.put("white", to=(0, 0, size - 1, size - 1))
        for i in range(size):
            img.put("black", (i, i))
            img.put("black", (size - 1 - i, i))
        return img

    def _on_close_press(self, event: tk.Event) -> str | None:
        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index(f"@{event.x},{event.y}")
            tab_id = self.tabs()[index]
            if tab_id in self.protected:
                return "break"
            self.state(["pressed"])
            self._active = index
            return "break"
        return None

    def _on_close_release(self, event: tk.Event) -> None:
        if not self.instate(["pressed"]):
            return
        element = self.identify(event.x, event.y)
        index = self.index(f"@{event.x},{event.y}")
        if "close" in element and self._active == index:
            tab_id = self.tabs()[index]
            if tab_id in self.protected:
                self.state(["!pressed"])
                self._active = None
                return
            self._closing_tab = tab_id
            self.event_generate("<<NotebookTabClosed>>")
            if tab_id in self.tabs():
                try:
                    self.forget(tab_id)
                except tk.TclError:
                    pass
        self.state(["!pressed"])
        self._active = None

    # --- Drag and detach functionality ---------------------------------

    def _on_tab_press(self, event: tk.Event) -> None:
        """Record which tab is being clicked for potential dragging."""
        if "label" in self.identify(event.x, event.y):
            try:
                self._drag_tab = self.index(f"@{event.x},{event.y}")
            except tk.TclError:
                self._drag_tab = None
            self._dragging = False

    def _on_tab_motion(self, _event: tk.Event) -> None:
        if self._drag_tab is not None:
            self._dragging = True

    def _on_tab_release(self, event: tk.Event) -> None:
        if self._drag_tab is None or not self._dragging:
            self._drag_tab = None
            self._dragging = False
            return

        tab_id = self.tabs()[self._drag_tab]
        widget = self.nametowidget(tab_id)
        text = self.tab(tab_id, "text")
        target: tk.Widget | None = self.winfo_containing(event.x_root, event.y_root)
        while target and not isinstance(target, ClosableNotebook):
            target = target.master
        if target is self:
            # Dropped back on the original notebook
            self._drag_tab = None
            self._dragging = False
            return

        self.forget(tab_id)
        if isinstance(target, ClosableNotebook):
            target.add(widget, text=text)
        else:
            self._create_detached_window(widget, text, event.x_root, event.y_root)
        self._drag_tab = None
        self._dragging = False

    def _create_detached_window(self, widget: tk.Widget, text: str, x: int, y: int) -> None:
        """Create a new window containing the dragged tab."""
        win = tk.Toplevel(self)
        nb = ClosableNotebook(win)
        nb.pack(fill=tk.BOTH, expand=True)
        nb.add(widget, text=text)
        win.geometry(f"+{x}+{y}")
        win.title(text)

