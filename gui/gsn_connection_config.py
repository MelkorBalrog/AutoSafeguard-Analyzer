"""Configuration dialog for editing GSN connections."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict

from gsn import GSNDiagram, GSNNode


class GSNConnectionConfig(tk.Toplevel):
    """Simple dialog to edit or delete a GSN relationship."""

    def __init__(self, master, parent: GSNNode, child: GSNNode, diagram: GSNDiagram):
        super().__init__(master)
        self.title("Edit Connection")
        self.parent = parent
        self.child = child
        self.diagram = diagram

        nodes = list(diagram._traverse())
        self._label_to_node: Dict[str, GSNNode] = {
            f"{n.user_name} ({n.unique_id})": n for n in nodes
        }

        ttk.Label(self, text="Parent:").grid(row=0, column=0, sticky="w")
        self.parent_var = tk.StringVar()
        parent_label = next(k for k, v in self._label_to_node.items() if v is parent)
        parent_cb = ttk.Combobox(self, textvariable=self.parent_var, values=list(self._label_to_node.keys()), state="readonly")
        self.parent_var.set(parent_label)
        parent_cb.grid(row=0, column=1, sticky="ew")

        ttk.Label(self, text="Child:").grid(row=1, column=0, sticky="w")
        self.child_var = tk.StringVar()
        child_label = next(k for k, v in self._label_to_node.items() if v is child)
        child_cb = ttk.Combobox(self, textvariable=self.child_var, values=list(self._label_to_node.keys()), state="readonly")
        self.child_var.set(child_label)
        child_cb.grid(row=1, column=1, sticky="ew")

        ttk.Label(self, text="Relation:").grid(row=2, column=0, sticky="w")
        self.rel_var = tk.StringVar()
        rel_cb = ttk.Combobox(self, textvariable=self.rel_var, values=["solved", "context"], state="readonly")
        self.rel_var.set("context" if child in parent.context_children else "solved")
        rel_cb.grid(row=2, column=1, sticky="ew")

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=4)
        ttk.Button(btn_frame, text="Delete", command=self._delete).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="OK", command=self._ok).pack(side=tk.LEFT)

        self.columnconfigure(1, weight=1)
        self.grab_set()
        self.resizable(False, False)

    def _node_for_label(self, label: str) -> GSNNode:
        return self._label_to_node[label]

    def _remove_connection(self, parent: GSNNode, child: GSNNode) -> None:
        if child in parent.children:
            parent.children.remove(child)
        if parent in child.parents:
            child.parents.remove(parent)
        if child in parent.context_children:
            parent.context_children.remove(child)

    def _ok(self) -> None:
        new_parent = self._node_for_label(self.parent_var.get())
        new_child = self._node_for_label(self.child_var.get())
        relation = self.rel_var.get()
        self._remove_connection(self.parent, self.child)
        if new_parent is not new_child:
            new_parent.add_child(new_child, relation=relation)
        self.destroy()

    def _delete(self) -> None:
        self._remove_connection(self.parent, self.child)
        self.destroy()
