"""Table view showing solutions for a safety & security case."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from analysis.safety_case import SafetyCase


class SafetyCaseTable(tk.Frame):
    """Display solution nodes of a :class:`SafetyCase` in a simple table."""

    def __init__(self, master, case: SafetyCase):
        if isinstance(master, tk.Toplevel):
            container = master
        else:
            container = master
        super().__init__(container)
        self.case = case
        if isinstance(master, tk.Toplevel):
            master.title(f"Safety Case: {case.name}")
            master.geometry("600x300")
            self.pack(fill=tk.BOTH, expand=True)

        columns = ("solution", "description", "work_product", "evidence_link", "notes")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        headers = {
            "solution": "Solution",
            "description": "Description",
            "work_product": "Work Product",
            "evidence_link": "Evidence Link",
            "notes": "Notes",
        }
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=120, stretch=True)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.populate()

    # ------------------------------------------------------------------
    def populate(self):
        """Fill the table with solution nodes from the case."""
        self.tree.delete(*self.tree.get_children())
        for sol in self.case.solutions:
            self.tree.insert(
                "",
                "end",
                values=(
                    sol.user_name,
                    getattr(sol, "description", ""),
                    getattr(sol, "work_product", ""),
                    getattr(sol, "evidence_link", ""),
                    getattr(sol, "manager_notes", ""),
                ),
            )
