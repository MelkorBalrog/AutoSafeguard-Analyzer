"""Custom ttk.Notebook widget with detachable tabs.

The widget behaves like a regular :class:`ttk.Notebook` but displays a close
button on the left of each tab. Tabs can also be dragged out of the notebook to
create a new floating window. Dragging a tab from a floating window back onto a
notebook re-attaches it to that notebook.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ClosableNotebook(ttk.Notebook):
    """Notebook widget with an 'x' button on the left side of each tab."""

    _style_initialized = False
    _close_img: tk.PhotoImage | None = None

    def __init__(self, master: tk.Widget | None = None, **kw):
        if not ClosableNotebook._style_initialized:
            # Create the close button image and register style elements only once
            ClosableNotebook._close_img = self._create_close_image()
            style = ttk.Style()
            style.element_create(
                "close",
                "image",
                ClosableNotebook._close_img,
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
            ClosableNotebook._style_initialized = True
        kw["style"] = "ClosableNotebook"
        super().__init__(master, **kw)
        self._active: int | None = None
        self._closing_tab: str | None = None
        self.protected: set[str] = set()
        self._drag_data: dict[str, int | None] = {"tab": None, "x": 0, "y": 0}
        self._dragging = False
        self.bind("<ButtonPress-1>", self._on_press, True)
        self.bind("<B1-Motion>", self._on_motion)
        self.bind("<ButtonRelease-1>", self._on_release, True)

    def _create_close_image(self, size: int = 10) -> tk.PhotoImage:
        img = tk.PhotoImage(width=size, height=size)
        img.put("white", to=(0, 0, size - 1, size - 1))
        for i in range(size):
            img.put("black", (i, i))
            img.put("black", (size - 1 - i, i))
        return img

    def _on_press(self, event: tk.Event) -> str | None:
        element = self.identify(event.x, event.y)
        try:
            index = self.index(f"@{event.x},{event.y}")
        except tk.TclError:
            index = None
        if "close" in element and index is not None:
            tab_id = self.tabs()[index]
            if tab_id in self.protected:
                return "break"
            self.state(["pressed"])
            self._active = index
            return "break"
        self._drag_data = {"tab": index, "x": event.x_root, "y": event.y_root}
        return None

    def _on_motion(self, event: tk.Event) -> None:
        if self._drag_data["tab"] is None:
            return
        dx = abs(event.x_root - self._drag_data["x"])
        dy = abs(event.y_root - self._drag_data["y"])
        if dx > 5 or dy > 5:
            self._dragging = True

    def _on_release(self, event: tk.Event) -> None:
        if self.instate(["pressed"]):
            element = self.identify(event.x, event.y)
            index = self.index(f"@{event.x},{event.y}")
            if "close" in element and self._active == index:
                tab_id = self.tabs()[index]
                if tab_id in self.protected:
                    self.state(["!pressed"])
                    self._active = None
                    self._reset_drag()
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
            self._reset_drag()
            return

        tab_index = self._drag_data["tab"]
        if tab_index is not None and self._dragging:
            try:
                tab_id = self.tabs()[tab_index]
            except IndexError:
                self._reset_drag()
                return
            widget = self.winfo_containing(event.x_root, event.y_root)
            while widget is not None and not isinstance(widget, ClosableNotebook):
                widget = widget.master
            if isinstance(widget, ClosableNotebook) and widget is not self:
                self._move_tab(tab_id, widget)
            else:
                self._detach_tab(tab_id, event.x_root, event.y_root)
        self._reset_drag()

    def _move_tab(self, tab_id: str, target: "ClosableNotebook") -> None:
        text = self.tab(tab_id, "text")
        child = self.nametowidget(tab_id)
        self.forget(tab_id)
        target.add(child, text=text)
        target.select(child)
        if isinstance(self.master, tk.Toplevel) and not self.tabs():
            self.master.destroy()

    def _detach_tab(self, tab_id: str, x: int, y: int) -> None:
        win = tk.Toplevel(self)
        win.geometry(f"+{x}+{y}")
        nb = ClosableNotebook(win)
        nb.pack(expand=True, fill="both")
        self._move_tab(tab_id, nb)

    def _reset_drag(self) -> None:
        self._drag_data = {"tab": None, "x": 0, "y": 0}
        self._dragging = False

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

