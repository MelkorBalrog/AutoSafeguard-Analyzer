"""Simple explorer window for GSN argumentation diagrams."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog

from gsn import GSNNode, GSNDiagram


class GSNExplorer(tk.Frame):
    """Manage and view GSN argumentation diagrams and their nodes."""

    def __init__(self, master, app=None):
        if isinstance(master, tk.Toplevel):
            container = master
        else:
            container = master
        super().__init__(container)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("GSN Explorer")
            master.geometry("350x400")
            self.pack(fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.tree = ttk.Treeview(tree_frame)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(btns, text="New Diagram", command=self.new_diagram).pack(side=tk.LEFT)
        ttk.Button(btns, text="Refresh", command=self.populate).pack(side=tk.LEFT, padx=5)

        self.populate()

    # ------------------------------------------------------------------
    def populate(self):
        """Fill the tree view with the available GSN diagrams."""
        self.tree.delete(*self.tree.get_children(""))
        if not self.app:
            return
        for idx, diag in enumerate(getattr(self.app, "gsn_diagrams", [])):
            root_id = self.tree.insert("", "end", f"diag_{idx}", text=diag.root.user_name)
            self._add_children(root_id, diag.root)

    # ------------------------------------------------------------------
    def _add_children(self, parent_id, node: GSNNode):
        for child in node.children:
            child_id = self.tree.insert(parent_id, "end", text=child.user_name, values=(child.node_type,))
            self._add_children(child_id, child)

    # ------------------------------------------------------------------
    def new_diagram(self):
        """Create a new GSN diagram with a single goal node as root."""
        if not self.app:
            return
        name = simpledialog.askstring("New GSN Diagram", "Root goal name:", parent=self)
        if not name:
            return
        root = GSNNode(name, "Goal")
        self.app.gsn_diagrams.append(GSNDiagram(root))
        self.populate()
