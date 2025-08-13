"""Explorer for safety & security cases derived from GSN diagrams."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog
from typing import Dict, Tuple


class DiagramSelectDialog(simpledialog.Dialog):  # pragma: no cover - requires tkinter
    """Dialog presenting a read-only list of diagram names."""

    def __init__(self, parent, title: str, options: list[str], initial: str | None = None):
        self.options = options
        self.initial = initial
        self.selection = ""
        super().__init__(parent, title)

    def body(self, master):  # pragma: no cover - requires tkinter
        ttk.Label(master, text="Diagram:").pack(padx=5, pady=5)
        self.var = tk.StringVar(
            value=self.initial if self.initial is not None else (self.options[0] if self.options else "")
        )
        combo = ttk.Combobox(
            master,
            textvariable=self.var,
            values=self.options,
            state="readonly",
        )
        combo.pack(padx=5, pady=5)
        return combo

    def apply(self):  # pragma: no cover - requires tkinter
        self.selection = self.var.get()

from analysis.safety_case import SafetyCaseLibrary, SafetyCase
from gui import messagebox


class SafetyCaseExplorer(tk.Frame):
    """Manage and browse safety & security cases."""

    def __init__(self, master, app=None, library: SafetyCaseLibrary | None = None):
        if isinstance(master, tk.Toplevel):
            container = master
        else:
            container = master
        super().__init__(container)
        self.app = app
        self.library = library or SafetyCaseLibrary()
        if isinstance(master, tk.Toplevel):
            master.title("Safety & Security Case Explorer")
            master.geometry("350x400")
            self.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(self)
        btns.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        ttk.Button(btns, text="Open", command=self.open_item).pack(side=tk.LEFT)
        ttk.Button(btns, text="New Case", command=self.new_case).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Edit", command=self.edit_case).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Delete", command=self.delete_case).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Refresh", command=self.populate).pack(side=tk.RIGHT)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.tree = ttk.Treeview(tree_frame)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.case_icon = self._create_icon("folder", "#b8860b")
        self.solution_icon = self._create_icon("circle", "#1e90ff")
        self.item_map: Dict[str, Tuple[str, object]] = {}

        self.tree.bind("<Double-1>", self._on_double_click)
        self.populate()

    # ------------------------------------------------------------------
    def populate(self):
        """Fill the tree with safety cases and their solutions."""
        self.item_map.clear()
        self.tree.delete(*self.tree.get_children(""))
        for case in self.library.list_cases():
            iid = self.tree.insert("", "end", text=case.name, image=self.case_icon)
            self.item_map[iid] = ("case", case)
            for sol in case.solutions:
                sid = self.tree.insert(iid, "end", text=sol.user_name, image=self.solution_icon)
                self.item_map[sid] = ("solution", sol)

    # ------------------------------------------------------------------
    def _available_diagrams(self):
        """Return a list of all GSN diagrams available in the application."""
        if not self.app:
            return []
        diagrams = list(getattr(self.app, "gsn_diagrams", []))
        for mod in getattr(self.app, "gsn_modules", []):
            diagrams.extend(self._collect_module_diagrams(mod))
        if not diagrams:
            diagrams = list(getattr(self.app, "all_gsn_diagrams", []))
        return diagrams

    # ------------------------------------------------------------------
    def _collect_module_diagrams(self, module):
        diagrams = list(getattr(module, "diagrams", []))
        for sub in getattr(module, "modules", []):
            diagrams.extend(self._collect_module_diagrams(sub))
        return diagrams

    # ------------------------------------------------------------------
    def new_case(self):
        """Create a new safety case derived from a GSN diagram."""
        diagrams = self._available_diagrams()
        if not diagrams:
            messagebox.showerror("New Case", "No GSN diagrams available")
            return
        name = simpledialog.askstring("New Safety Case", "Name:", parent=self)
        if not name:
            return
        diag_names = [d.root.user_name for d in diagrams]
        dlg = DiagramSelectDialog(self, "GSN Diagram", diag_names)
        diag_name = dlg.selection
        if not diag_name:
            return
        diag = next((d for d in diagrams if d.root.user_name == diag_name), None)
        if not diag:
            messagebox.showerror("New Case", "Diagram not found")
            return
        self.library.create_case(name, diag)
        self.populate()

    # ------------------------------------------------------------------
    def edit_case(self):
        """Rename the selected safety case or change its diagram."""
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ != "case":
            return
        new_name = simpledialog.askstring(
            "Rename Safety Case", "Name:", initialvalue=obj.name, parent=self
        )
        if not new_name:
            return
        diagrams = self._available_diagrams()
        diag_names = [d.root.user_name for d in diagrams]
        dlg = DiagramSelectDialog(
            self, "GSN Diagram", diag_names, obj.diagram.root.user_name
        )
        new_diag_name = dlg.selection
        if not new_diag_name:
            return
        new_diag = next((d for d in diagrams if d.root.user_name == new_diag_name), None)
        if not new_diag:
            messagebox.showerror("Edit Case", "Diagram not found")
            return
        obj.name = new_name
        obj.diagram = new_diag
        obj.collect_solutions()
        self.populate()

    # ------------------------------------------------------------------
    def delete_case(self):
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ != "case":
            return
        if messagebox.askokcancel("Delete", f"Delete '{obj.name}'?"):
            self.library.delete_case(obj)
            self.populate()

    # ------------------------------------------------------------------
    def open_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ == "case" and self.app:
            opener = getattr(self.app, "open_gsn_diagram", None)
            if opener:
                opener(obj.diagram)
        elif typ == "solution" and self.app:
            for case in self.library.cases:
                if obj in case.solutions:
                    opener = getattr(self.app, "open_gsn_diagram", None)
                    if opener:
                        opener(case.diagram)
                    break

    # ------------------------------------------------------------------
    def _on_double_click(self, event):
        self.open_item()

    # ------------------------------------------------------------------
    def _create_icon(self, shape: str, color: str = "black") -> tk.PhotoImage:
        """Return a simple 16x16 icon for treeview items."""
        size = 16
        img = tk.PhotoImage(width=size, height=size)
        img.put("white", to=(0, 0, size - 1, size - 1))
        c = color
        if shape == "circle":
            r = size // 2 - 2
            cx = cy = size // 2
            for y in range(size):
                for x in range(size):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                        img.put(c, (x, y))
        elif shape == "diamond":
            mid = size // 2
            for y in range(2, size - 2):
                span = mid - abs(mid - y)
                img.put(c, to=(mid - span, y, mid + span + 1, y + 1))
        elif shape == "rect":
            for x in range(3, size - 3):
                img.put(c, (x, 3))
                img.put(c, (x, size - 4))
            for y in range(3, size - 3):
                img.put(c, (3, y))
                img.put(c, (size - 4, y))
        elif shape == "folder":
            for x in range(1, size - 1):
                img.put(c, (x, 4))
                img.put(c, (x, size - 2))
            for y in range(4, size - 1):
                img.put(c, (1, y))
                img.put(c, (size - 2, y))
            for x in range(3, size - 3):
                img.put(c, (x, 2))
            img.put(c, to=(1, 3, size - 2, 4))
        return img
