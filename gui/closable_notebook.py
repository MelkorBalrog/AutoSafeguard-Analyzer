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

    # ------------------------------------------------------------------
    # Backwards compatible helpers
    # ------------------------------------------------------------------
    #
    # Older code as well as the unit tests in this repository expect the
    # notebook to expose ``_on_tab_press`` and ``_on_tab_release`` methods
    # that behave like the bound event handlers above.  The original file
    # was refactored to use the shorter ``_on_press``/``_on_release`` names
    # but the helper methods were accidentally dropped.  Without them the
    # tests fail with ``AttributeError`` and dragging a tab programmatically
    # is impossible.  Provide tiny wrappers so the old API continues to
    # work.

    def _on_tab_press(self, event: tk.Event) -> str | None:  # pragma: no cover - thin wrapper
        return self._on_press(event)

    def _on_tab_release(self, event: tk.Event) -> None:  # pragma: no cover - thin wrapper
        self._on_release(event)

    def _on_tab_motion(self, event: tk.Event) -> None:  # pragma: no cover - thin wrapper
        self._on_motion(event)

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
        # Reparent the tab's child widget to the target notebook before adding.
        # ``tk::unsupported::reparent`` is available on most Tk builds but the
        # exact command name differs across platforms.  Try the known variants
        # and ignore any errors so that platforms without the command still
        # proceed.
        # ``tk::unsupported::reparent`` expects platform specific arguments.
        # Some builds use window path names while others require the window
        # identifier returned by ``winfo_id``.  Try both forms to cover the
        # common variants and silently continue if the command is unavailable.
        reparented = False
        for cmd in (
            ("::tk::unsupported::reparent", child.winfo_id(), target.winfo_id()),
            ("::tk::unsupported::reparent", child._w, target._w),
            ("tk", "unsupported", "reparent", child.winfo_id(), target.winfo_id()),
            ("tk", "unsupported", "reparent", child._w, target._w),
        ):
            try:
                child.tk.call(*cmd)
                reparented = True
                break
            except tk.TclError:
                continue
        if reparented:
            child.master = target  # keep Python's widget hierarchy in sync
            target.add(child, text=text)
            target.select(child)
        else:
            # If reparenting is unsupported we simply abort the move.
            # Re-insert the tab into its original notebook so the widget
            # remains accessible instead of raising a TclError.
            self.add(child, text=text)
            self.select(child)
            return
        if isinstance(self.master, tk.Toplevel) and not self.tabs():
            self.master.destroy()

    def _detach_tab(self, tab_id: str, x: int, y: int) -> None:
        self.update_idletasks()
        width = self.winfo_width() or 200
        height = self.winfo_height() or 200
        win = tk.Toplevel(self)
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = max(min(x, screen_w - width), 0)
        y = max(min(y, screen_h - height), 0)
        win.geometry(f"{width}x{height}+{x}+{y}")
        nb = ClosableNotebook(win)
        nb.pack(expand=True, fill="both")
        # ``tk::unsupported::reparent`` requires the target widget to be
        # realised.  Simply updating the notebook's idle tasks is not
        # sufficient on some platforms where the toplevel must be fully
        # mapped before reparenting succeeds.  Updating the window itself
        # guarantees the required window id exists so the tab is detached
        # into a visible notebook instead of an empty toplevel.
        win.update()
        self._move_tab(tab_id, nb)

    def _reset_drag(self) -> None:
        self._drag_data = {"tab": None, "x": 0, "y": 0}
        self._dragging = False
