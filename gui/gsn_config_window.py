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
        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.name_var = tk.StringVar(value=node.user_name)
        tk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=4)
        tk.Label(self, text="Description:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.desc_var = tk.StringVar(value=getattr(node, "description", ""))
        tk.Entry(self, textvariable=self.desc_var).grid(row=1, column=1, padx=4, pady=4)
        btns = ttk.Frame(self)
        btns.grid(row=2, column=0, columnspan=2, pady=4)
        ttk.Button(btns, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=4)
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _on_ok(self):
        self.node.user_name = self.name_var.get()
        self.node.description = self.desc_var.get()
        self.destroy()
