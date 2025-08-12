"""Simple explorer window for GSN argumentation diagrams."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog

from gsn import GSNNode, GSNDiagram, GSNModule


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

        self.item_map: dict[str, tuple[str, object]] = {}

        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(btns, text="New Module", command=self.new_module).pack(side=tk.LEFT)
        ttk.Button(btns, text="New Diagram", command=self.new_diagram).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Rename", command=self.rename_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Refresh", command=self.populate).pack(side=tk.RIGHT)

        self.populate()

    # ------------------------------------------------------------------
    def populate(self):
        """Fill the tree view with the available GSN diagrams."""
        self.item_map.clear()
        self.tree.delete(*self.tree.get_children(""))
        if not self.app:
            return
        # modules at root
        for mod in getattr(self.app, "gsn_modules", []):
            mod_id = self.tree.insert("", "end", text=mod.name)
            self.item_map[mod_id] = ("module", mod)
            self._add_module_children(mod_id, mod)
        # diagrams not in any module
        for diag in getattr(self.app, "gsn_diagrams", []):
            diag_id = self.tree.insert("", "end", text=diag.root.user_name)
            self.item_map[diag_id] = ("diagram", diag)
            self._add_node_children(diag_id, diag.root)

    # ------------------------------------------------------------------
    def _add_module_children(self, parent_id: str, module: GSNModule):
        for sub in module.modules:
            sub_id = self.tree.insert(parent_id, "end", text=sub.name)
            self.item_map[sub_id] = ("module", sub)
            self._add_module_children(sub_id, sub)
        for diag in module.diagrams:
            diag_id = self.tree.insert(parent_id, "end", text=diag.root.user_name)
            self.item_map[diag_id] = ("diagram", diag)
            self._add_node_children(diag_id, diag.root)

    # ------------------------------------------------------------------
    def _add_node_children(self, parent_id, node: GSNNode):
        for child in node.children:
            child_id = self.tree.insert(parent_id, "end", text=child.user_name)
            self.item_map[child_id] = ("node", child)
            self._add_node_children(child_id, child)

    # ------------------------------------------------------------------
    def new_diagram(self):
        """Create a new GSN diagram with a single goal node as root."""
        if not self.app:
            return
        name = simpledialog.askstring("New GSN Diagram", "Root goal name:", parent=self)
        if not name:
            return
        root = GSNNode(name, "Goal")
        diag = GSNDiagram(root)
        self.app.gsn_diagrams.append(diag)
        sel = self.tree.selection()
        if sel:
            typ, obj = self.item_map.get(sel[0], (None, None))
            if typ == "module":
                obj.diagrams.append(diag)
        self.populate()

    # ------------------------------------------------------------------
    def new_module(self):
        if not self.app:
            return
        name = simpledialog.askstring("New GSN Module", "Module name:", parent=self)
        if not name:
            return
        module = GSNModule(name)
        sel = self.tree.selection()
        if sel:
            typ, obj = self.item_map.get(sel[0], (None, None))
            if typ == "module":
                obj.modules.append(module)
                self.populate()
                return
        self.app.gsn_modules.append(module)
        self.populate()

    # ------------------------------------------------------------------
    def rename_item(self):
        if not self.app:
            return
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ == "module":
            new = simpledialog.askstring("Rename Module", "Name:", initialvalue=obj.name, parent=self)
            if new:
                obj.name = new
        elif typ == "diagram":
            new = simpledialog.askstring("Rename Diagram", "Name:", initialvalue=obj.root.user_name, parent=self)
            if new:
                obj.root.user_name = new
        self.populate()

    # ------------------------------------------------------------------
    def delete_item(self):
        if not self.app:
            return
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        typ, obj = self.item_map.get(item, (None, None))
        if typ == "diagram":
            parent = self._find_parent_module(item)
            if parent:
                parent.diagrams.remove(obj)
            if obj in self.app.gsn_diagrams:
                self.app.gsn_diagrams.remove(obj)
        elif typ == "module":
            parent = self._find_parent_module(item)
            if parent is None:
                self.app.gsn_modules.remove(obj)
            else:
                parent.modules.remove(obj)
            # remove diagrams from global list recursively
            for d in self._collect_diagrams(obj):
                if d in self.app.gsn_diagrams:
                    self.app.gsn_diagrams.remove(d)
        self.populate()

    # ------------------------------------------------------------------
    def _collect_diagrams(self, module: GSNModule):
        for d in module.diagrams:
            yield d
        for m in module.modules:
            yield from self._collect_diagrams(m)

    # ------------------------------------------------------------------
    def _find_parent_module(self, item: str):
        parent = self.tree.parent(item)
        while parent:
            typ, obj = self.item_map.get(parent, (None, None))
            if typ == "module":
                return obj
            parent = self.tree.parent(parent)
        return None
