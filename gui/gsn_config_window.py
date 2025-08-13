"""Configuration dialog for editing GSN node properties."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gsn import GSNNode


class GSNElementConfig(tk.Toplevel):
    """Simple dialog to edit a GSN element's name and description."""

    def __init__(self, master, node: GSNNode):
        super().__init__(master)
        self.node = node
        self.title("Edit GSN Element")
        self.geometry("400x200")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.name_var = tk.StringVar(value=node.user_name)
        tk.Entry(self, textvariable=self.name_var, width=40).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        tk.Label(self, text="Description:").grid(row=1, column=0, sticky="ne", padx=4, pady=4)
        self.desc_text = tk.Text(self, width=40, height=5)
        self.desc_text.insert("1.0", getattr(node, "description", ""))
        self.desc_text.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        btns = ttk.Frame(self)
        btns.grid(row=2, column=0, columnspan=2, pady=4)
        ttk.Button(btns, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=4)
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _on_ok(self):
        self.node.user_name = self.name_var.get()
        self.node.description = self.desc_text.get("1.0", tk.END).strip()
        self.destroy()
