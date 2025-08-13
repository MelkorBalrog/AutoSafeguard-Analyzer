"""Explorer window for safety governance diagrams."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog
from gui import messagebox
from dataclasses import dataclass, field
from typing import List, Dict

from analysis.safety_management import SafetyManagementToolbox, GovernanceModule


class SafetyManagementExplorer(tk.Frame):
    """Browse and organise safety governance diagrams in folders."""

    def __init__(self, master, app=None, toolbox: SafetyManagementToolbox | None = None):
        if isinstance(master, tk.Toplevel):
            container = master
        else:
            container = master
        super().__init__(container)
        self.app = app
        self.toolbox = toolbox or SafetyManagementToolbox()
        if isinstance(master, tk.Toplevel):
            master.title("Safety & Security Management Explorer")
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

        self.folder_icon = self._create_icon("folder", "#b8860b")
        self.diagram_icon = self._create_icon("rect", "#4682b4")
        self.item_map: Dict[str, tuple[str, object]] = {}

        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(btns, text="Open", command=self.open_item).pack(side=tk.LEFT)
        ttk.Button(btns, text="New Folder", command=self.new_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="New Diagram", command=self.new_diagram).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Rename", command=self.rename_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Refresh", command=self.populate).pack(side=tk.RIGHT)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<ButtonRelease-1>", self._on_drop)
        self.populate()

    # ------------------------------------------------------------------
    def populate(self):
        """Fill the tree with folders and diagrams."""
        self.item_map.clear()
        self.tree.delete(*self.tree.get_children(""))
        self.toolbox.list_diagrams()

        def _add_module(parent: str, mod: GovernanceModule) -> None:
            for sub in mod.modules:
                sub_id = self.tree.insert(parent, "end", text=sub.name, image=self.folder_icon)
                self.item_map[sub_id] = ("module", sub)
                _add_module(sub_id, sub)
            for name in mod.diagrams:
                diag_id = self.tree.insert(parent, "end", text=name, image=self.diagram_icon)
                self.item_map[diag_id] = ("diagram", name)

        for mod in self.toolbox.modules:
            mod_id = self.tree.insert("", "end", text=mod.name, image=self.folder_icon)
            self.item_map[mod_id] = ("module", mod)
            _add_module(mod_id, mod)

        for name in sorted(self.toolbox.diagrams.keys()):
            if not self._in_any_module(name, self.toolbox.modules):
                iid = self.tree.insert("", "end", text=name, image=self.diagram_icon)
                self.item_map[iid] = ("diagram", name)

    # ------------------------------------------------------------------
    def new_folder(self):
        name = simpledialog.askstring("New Folder", "Name:", parent=self)
        if not name:
            return
        folder = GovernanceModule(name)
        sel = self.tree.selection()
        if sel:
            typ, obj = self.item_map.get(sel[0], (None, None))
            if typ == "module":
                obj.modules.append(folder)
            else:
                self.toolbox.modules.append(folder)
        else:
            self.toolbox.modules.append(folder)
        self.populate()

    # ------------------------------------------------------------------
    def new_diagram(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("New Diagram", "Please select a folder for the diagram")
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ != "module":
            messagebox.showerror("New Diagram", "Please select a folder for the diagram")
            return
        name = simpledialog.askstring("New Diagram", "Name:", parent=self)
        if not name:
            return
        self.toolbox.create_diagram(name)
        obj.diagrams.append(name)
        self.populate()

    # ------------------------------------------------------------------
    def rename_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ != "diagram":
            return
        new = simpledialog.askstring("Rename Diagram", "Name:", initialvalue=obj, parent=self)
        if not new or new == obj:
            return
        self.toolbox.rename_diagram(obj, new)
        self._replace_name_in_modules(obj, new, self.toolbox.modules)
        self.populate()

    # ------------------------------------------------------------------
    def delete_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ == "diagram":
            self.toolbox.delete_diagram(obj)
            self._remove_name(obj, self.toolbox.modules)
        elif typ == "module":
            if obj.modules or obj.diagrams:
                return
            parent = self.tree.parent(sel[0])
            if parent:
                ptyp, pobj = self.item_map.get(parent, (None, None))
                if ptyp == "module":
                    pobj.modules.remove(obj)
            else:
                self.toolbox.modules.remove(obj)
        self.populate()

    # ------------------------------------------------------------------
    def open_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ != "diagram":
            return
        diag_id = self.toolbox.diagrams.get(obj)
        if diag_id and self.app:
            self.app.open_arch_window(diag_id)

    # ------------------------------------------------------------------
    def _on_double_click(self, _event):  # pragma: no cover - UI event
        self.open_item()

    # ------------------------------------------------------------------
    def _on_drag_start(self, event):  # pragma: no cover - UI event
        """Record the tree item being dragged."""
        iid = self.tree.identify_row(event.y)
        self._drag_item = iid if iid else None

    # ------------------------------------------------------------------
    def _on_drop(self, event):  # pragma: no cover - UI event
        """Handle dropping of a tree item onto another item or the root."""
        if not getattr(self, "_drag_item", None):
            return

        target = self.tree.identify_row(event.y)
        if target == self._drag_item:
            self._drag_item = None
            return

        item_type, item_obj = self.item_map.get(self._drag_item, (None, None))
        tgt_type, tgt_obj = self.item_map.get(target, (None, None))
        if tgt_type == "diagram":
            target = self.tree.parent(target)
            tgt_type, tgt_obj = self.item_map.get(target, (None, None))

        if target and tgt_type == "module":
            parent_mod = tgt_obj
            new_parent = target
        else:
            parent_mod = None
            new_parent = ""

        self.tree.move(self._drag_item, new_parent, "end")

        if item_type == "diagram":
            self._remove_name(item_obj, self.toolbox.modules)
            if parent_mod:
                parent_mod.diagrams.append(item_obj)
        elif item_type == "module":
            self._remove_module(item_obj, self.toolbox.modules)
            if parent_mod:
                parent_mod.modules.append(item_obj)
            else:
                self.toolbox.modules.append(item_obj)

        self._drag_item = None

    # ------------------------------------------------------------------
    def _in_any_module(self, name: str, mods: List[GovernanceModule]) -> bool:
        for mod in mods:
            if name in mod.diagrams or self._in_any_module(name, mod.modules):
                return True
        return False

    def _replace_name_in_modules(self, old: str, new: str, mods: List[GovernanceModule]) -> None:
        for mod in mods:
            mod.diagrams = [new if d == old else d for d in mod.diagrams]
            self._replace_name_in_modules(old, new, mod.modules)

    def _remove_name(self, name: str, mods: List[GovernanceModule]) -> None:
        for mod in mods:
            if name in mod.diagrams:
                mod.diagrams.remove(name)
            self._remove_name(name, mod.modules)

    def _remove_module(self, target: GovernanceModule, mods: List[GovernanceModule]) -> bool:
        for mod in mods:
            if mod is target:
                mods.remove(mod)
                return True
            if self._remove_module(target, mod.modules):
                return True
        return False

    # ------------------------------------------------------------------
    def _create_icon(self, shape: str, color: str = "black"):
        """Create a tiny tkinter drawing for treeview icons."""
        img = tk.PhotoImage(width=16, height=16)
        if shape == "folder":
            img.put(color, to=(0, 4, 15, 15))
            img.put("white", to=(3, 0, 15, 5))
        elif shape == "rect":
            img.put(color, to=(1, 1, 15, 15))
        else:
            img.put(color, to=(1, 1, 15, 15))
        return img
