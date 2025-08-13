"""Configuration dialog for editing GSN node properties."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gsn import GSNNode, GSNDiagram

WORK_PRODUCTS = [
    "Architectural Diagram",
    "Hazard & Cyber Analysis",
    "Risk Assessment",
    "Safety Analysis",
]


class GSNElementConfig(tk.Toplevel):
    """Simple dialog to edit a GSN element's properties."""

    def __init__(self, master, node: GSNNode, diagram: GSNDiagram):
        super().__init__(master)
        self.node = node
        self.diagram = diagram
        self.title("Edit GSN Element")
        self.geometry("400x280")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.name_var = tk.StringVar(value=node.user_name)
        tk.Entry(self, textvariable=self.name_var, width=40).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        tk.Label(self, text="Description:").grid(row=1, column=0, sticky="ne", padx=4, pady=4)
        self.desc_text = tk.Text(self, width=40, height=5)
        self.desc_text.insert("1.0", getattr(node, "description", ""))
        self.desc_text.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")

        self.work_var = tk.StringVar(value=getattr(node, "work_product", ""))
        self.link_var = tk.StringVar(value=getattr(node, "evidence_link", ""))
        row = 2
        if node.node_type == "Solution":
            tk.Label(self, text="Work Product:").grid(
                row=row, column=0, sticky="e", padx=4, pady=4
            )
            ttk.Combobox(
                self,
                textvariable=self.work_var,
                values=WORK_PRODUCTS,
                state="readonly",
            ).grid(row=row, column=1, padx=4, pady=4, sticky="ew")
            row += 1
            tk.Label(self, text="Evidence Link:").grid(
                row=row, column=0, sticky="e", padx=4, pady=4
            )
            tk.Entry(self, textvariable=self.link_var, width=40).grid(
                row=row, column=1, padx=4, pady=4, sticky="ew"
            )
            row += 1
        btns = ttk.Frame(self)
        btns.grid(row=row, column=0, columnspan=2, pady=4)
        ttk.Button(btns, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=4)
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _on_ok(self):
        self.node.user_name = self.name_var.get()
        self.node.description = self.desc_text.get("1.0", tk.END).strip()
        if self.node.node_type == "Solution":
            self.node.work_product = self.work_var.get()
            self.node.evidence_link = self.link_var.get()
            # search for existing solution with same work product
            for n in self.diagram.nodes:
                if (
                    n is not self.node
                    and n.node_type == "Solution"
                    and getattr(n, "work_product", "") == self.node.work_product
                ):
                    original = n if n.is_primary_instance else n.original
                    self.node.user_name = original.user_name
                    self.node.description = getattr(original, "description", "")
                    self.node.unique_id = original.unique_id
                    self.node.original = original
                    self.node.is_primary_instance = False
                    break
            else:
                self.node.is_primary_instance = True
                self.node.original = self.node
        self.destroy()
