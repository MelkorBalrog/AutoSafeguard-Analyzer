"""Search toolbox for finding nodes within the AutoML model."""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

from gui import messagebox


class SearchToolbox(tk.Toplevel):
    """Provide simple text-based search across model nodes."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.title("Search")

        self.search_var = tk.StringVar()
        self.case_var = tk.BooleanVar(value=False)
        self.regex_var = tk.BooleanVar(value=False)
        self.results: list = []

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(frame, text="Find:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.search_var)
        entry.grid(row=0, column=1, sticky="ew")
        entry.focus_set()

        btn = ttk.Button(frame, text="Search", command=self._run_search)
        btn.grid(row=0, column=2, padx=(4, 0))

        opts = ttk.Frame(frame)
        opts.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))
        ttk.Checkbutton(opts, text="Case sensitive", variable=self.case_var).pack(
            side=tk.LEFT
        )
        ttk.Checkbutton(opts, text="Regular expression", variable=self.regex_var).pack(
            side=tk.LEFT
        )

        self.results_box = tk.Listbox(frame, height=10)
        self.results_box.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        self.results_box.bind("<Double-1>", self._open_selected)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        self.transient(master)
        self.grab_set()

    def _run_search(self) -> None:
        pattern = self.search_var.get().strip()
        if not pattern:
            return
        flags = 0 if self.case_var.get() else re.IGNORECASE
        try:
            regex = re.compile(pattern if self.regex_var.get() else re.escape(pattern), flags)
        except re.error as exc:  # pragma: no cover - user feedback path
            messagebox.showerror("Search", f"Invalid pattern: {exc}")
            return

        self.results_box.delete(0, tk.END)
        self.results = []
        root_node = getattr(self.app, "root_node", None)
        nodes = self.app.get_all_nodes(root_node) if root_node else []
        for node in nodes:
            text = f"{node.user_name}\n{getattr(node, 'description', '')}"
            if regex.search(text):
                self.results_box.insert(tk.END, f"{node.node_type}: {node.user_name}")
                self.results.append(node)

    def _open_selected(self, _event=None) -> None:
        if not self.results_box.curselection():
            return
        node = self.results[self.results_box.curselection()[0]]
        self.app.selected_node = node
        try:  # pragma: no cover - GUI integration
            self.app.edit_selected()
        except Exception:
            pass
