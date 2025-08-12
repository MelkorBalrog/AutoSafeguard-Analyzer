"""Custom ttk.Notebook widget with close buttons on each tab."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ClosableNotebook(ttk.Notebook):
    """Notebook widget with an 'x' button on each tab to close it."""

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
                                                    ("Notebook.label", {"side": "left", "sticky": ""}),
                                                    ("close", {"side": "left", "sticky": ""}),
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
        self.bind("<ButtonPress-1>", self._on_close_press, True)
        self.bind("<ButtonRelease-1>", self._on_close_release)

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

