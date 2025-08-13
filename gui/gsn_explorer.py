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

        # simple icons so different elements are visually distinct
        self.module_icon = self._create_icon("folder", "#b8860b")
        self.diagram_icon = self._create_icon("rect", "#4682b4")
        self.node_icons = {
            "Goal": self._create_icon("rect", "#2e8b57"),
            "Strategy": self._create_icon("diamond", "#8b008b"),
            "Solution": self._create_icon("circle", "#1e90ff"),
            "Assumption": self._create_icon("rect", "#b22222"),
            "Justification": self._create_icon("rect", "#ff8c00"),
            "Context": self._create_icon("rect", "#696969"),
            "Module": self.module_icon,
        }
        self.default_node_icon = self._create_icon("rect")
        self.item_map: dict[str, tuple[str, object]] = {}

        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(btns, text="Open", command=self.open_item).pack(side=tk.LEFT)
        ttk.Button(btns, text="New Module", command=self.new_module).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="New Diagram", command=self.new_diagram).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Rename", command=self.rename_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Refresh", command=self.populate).pack(side=tk.RIGHT)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
        # drag and drop support
        self.drag_item: str | None = None
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_end)
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
            mod_id = self.tree.insert("", "end", text=mod.name, image=self.module_icon)
            self.item_map[mod_id] = ("module", mod)
            self._add_module_children(mod_id, mod)
        # diagrams not in any module
        for diag in getattr(self.app, "gsn_diagrams", []):
            diag_id = self.tree.insert("", "end", text=diag.root.user_name, image=self.diagram_icon)
            self.item_map[diag_id] = ("diagram", diag)
            self._add_diagram_children(diag_id, diag)

    # ------------------------------------------------------------------
    def refresh(self):
        """Refresh the explorer view to reflect the current model state."""
        self.populate()

    # ------------------------------------------------------------------
    def _add_module_children(self, parent_id: str, module: GSNModule):
        for sub in module.modules:
            sub_id = self.tree.insert(parent_id, "end", text=sub.name, image=self.module_icon)
            self.item_map[sub_id] = ("module", sub)
            self._add_module_children(sub_id, sub)
        for diag in module.diagrams:
            diag_id = self.tree.insert(parent_id, "end", text=diag.root.user_name, image=self.diagram_icon)
            self.item_map[diag_id] = ("diagram", diag)
            self._add_diagram_children(diag_id, diag)

    # ------------------------------------------------------------------
    def _add_diagram_children(self, diag_id: str, diagram: GSNDiagram) -> None:
        """Insert all nodes of *diagram* below *diag_id*.

        The previous implementation only traversed nodes reachable from the
        diagram's root which meant unconnected nodes were omitted from the
        explorer view.  Iterate over the diagram's ``nodes`` collection to
        ensure that even orphaned elements become visible.
        """

        visited_ids: set[int] = set()

        def _add_node(parent_id: str, node: GSNNode) -> None:
            visited_ids.add(id(node))
            for child in node.children:
                icon = self.node_icons.get(child.node_type, self.default_node_icon)
                child_id = self.tree.insert(parent_id, "end", text=child.user_name, image=icon)
                self.item_map[child_id] = ("node", child)
                _add_node(child_id, child)

        # start with the root node and then append any remaining nodes
        _add_node(diag_id, diagram.root)
        for node in diagram.nodes:
            if id(node) not in visited_ids:
                icon = self.node_icons.get(node.node_type, self.default_node_icon)
                node_id = self.tree.insert(diag_id, "end", text=node.user_name, image=icon)
                self.item_map[node_id] = ("node", node)
                _add_node(node_id, node)

    # ------------------------------------------------------------------
    def new_diagram(self):
        """Create a new GSN diagram with a single goal node as root."""
        if not self.app:
            return
        name = simpledialog.askstring("New GSN Diagram", "Root goal name:", parent=self)
        if not name:
            return
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
        root = GSNNode(name, "Goal")
        diag = GSNDiagram(root)
        sel = self.tree.selection()
        if sel:
            typ, obj = self.item_map.get(sel[0], (None, None))
            if typ == "module":
                obj.diagrams.append(diag)
            else:
                self.app.gsn_diagrams.append(diag)
        else:
            self.app.gsn_diagrams.append(diag)
        self.populate()

    # ------------------------------------------------------------------
    def new_module(self):
        if not self.app:
            return
        name = simpledialog.askstring("New GSN Module", "Module name:", parent=self)
        if not name:
            return
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
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
            # Renaming modules is currently not supported to avoid breaking
            # references in GSN diagrams.
            return
        elif typ == "diagram":
            new = simpledialog.askstring("Rename Diagram", "Name:", initialvalue=obj.root.user_name, parent=self)
            if new:
                undo = getattr(self.app, "push_undo_state", None)
                if undo:
                    undo()
                obj.root.user_name = new
        elif typ == "node":
            if getattr(obj, "node_type", "") == "Module":
                return
            new = simpledialog.askstring(
                "Rename Node", "Name:", initialvalue=obj.user_name, parent=self
            )
            if new:
                undo = getattr(self.app, "push_undo_state", None)
                if undo:
                    undo()
                obj.user_name = new
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
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
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
        elif typ == "node":
            diagram = self._find_parent_diagram(item)
            if diagram and obj in diagram.nodes:
                diagram.nodes.remove(obj)
                if obj is diagram.root and diagram.nodes:
                    diagram.root = diagram.nodes[0]
            for parent in list(obj.parents):
                if obj in parent.children:
                    parent.children.remove(obj)
                if obj in parent.context_children:
                    parent.context_children.remove(obj)
            for child in list(obj.children):
                if obj in child.parents:
                    child.parents.remove(obj)
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

    # ------------------------------------------------------------------
    def _find_parent_diagram(self, item: str):
        parent = self.tree.parent(item)
        while parent:
            typ, obj = self.item_map.get(parent, (None, None))
            if typ == "diagram":
                return obj
            parent = self.tree.parent(parent)
        return None

    # ------------------------------------------------------------------
    def _on_right_click(self, event):  # pragma: no cover - requires tkinter
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.tree.selection_set(item)
        menu = tk.Menu(self.tree, tearoff=0)
        typ, _obj = self.item_map.get(item, (None, None))
        if typ == "module":
            menu.add_command(label="New Module", command=self.new_module)
            menu.add_command(label="New Diagram", command=self.new_diagram)
            menu.add_separator()
            menu.add_command(label="Rename", command=self.rename_item)
            menu.add_command(label="Delete", command=self.delete_item)
        elif typ == "diagram":
            menu.add_command(label="Open", command=self.open_item)
            menu.add_separator()
            menu.add_command(label="Rename", command=self.rename_item)
            menu.add_command(label="Delete", command=self.delete_item)
        elif typ == "node":
            menu.add_command(label="Rename", command=self.rename_item)
            menu.add_command(label="Delete", command=self.delete_item)
        else:
            menu.add_command(label="Refresh", command=self.populate)
        menu.tk_popup(event.x_root, event.y_root)

    # ------------------------------------------------------------------
    def _on_drag_start(self, event):
        """Record the item being dragged."""
        self.drag_item = self.tree.identify_row(event.y)

    # ------------------------------------------------------------------
    def _on_drag_end(self, event):
        """Handle dropping of an item onto a new parent."""
        if not self.app or not self.drag_item:
            self.drag_item = None
            return
        target = self.tree.identify_row(event.y)
        if target == self.drag_item:
            self.drag_item = None
            return
        drag_type, drag_obj = self.item_map.get(self.drag_item, (None, None))
        if drag_type not in ("diagram", "module"):
            self.drag_item = None
            return
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
        parent_module = None
        if target:
            target_type, target_obj = self.item_map.get(target, (None, None))
            if target_type == "module":
                parent_module = target_obj
            else:
                parent_module = self._find_parent_module(target)
        if drag_type == "diagram":
            if parent_module is None:
                self._move_diagram_to_root(drag_obj)
            else:
                self._move_diagram_to_module(drag_obj, parent_module)
        elif drag_type == "module":
            if parent_module is None:
                self._move_module_to_root(drag_obj)
            elif not self._is_descendant_module(drag_obj, parent_module):
                self._move_module_to_module(drag_obj, parent_module)
        self.drag_item = None
        self.populate()

    # ------------------------------------------------------------------
    def _remove_diagram_from_all_modules(self, diag: GSNDiagram, modules=None):
        modules = modules or getattr(self.app, "gsn_modules", [])
        for mod in modules:
            if diag in mod.diagrams:
                mod.diagrams.remove(diag)
                return True
            if self._remove_diagram_from_all_modules(diag, mod.modules):
                return True
        return False

    # ------------------------------------------------------------------
    def _remove_module_from_parent(self, module: GSNModule, modules=None):
        modules = modules or getattr(self.app, "gsn_modules", [])
        for mod in modules:
            if module in mod.modules:
                mod.modules.remove(module)
                return True
            if self._remove_module_from_parent(module, mod.modules):
                return True
        return False

    # ------------------------------------------------------------------
    def _move_diagram_to_module(self, diag: GSNDiagram, module: GSNModule):
        if diag in getattr(self.app, "gsn_diagrams", []):
            self.app.gsn_diagrams.remove(diag)
        else:
            self._remove_diagram_from_all_modules(diag)
        module.diagrams.append(diag)

    # ------------------------------------------------------------------
    def _move_diagram_to_root(self, diag: GSNDiagram):
        if diag not in getattr(self.app, "gsn_diagrams", []):
            self._remove_diagram_from_all_modules(diag)
            self.app.gsn_diagrams.append(diag)

    # ------------------------------------------------------------------
    def _move_module_to_module(self, module: GSNModule, parent: GSNModule):
        if module in getattr(self.app, "gsn_modules", []):
            self.app.gsn_modules.remove(module)
        else:
            self._remove_module_from_parent(module)
        parent.modules.append(module)

    # ------------------------------------------------------------------
    def _move_module_to_root(self, module: GSNModule):
        if module not in getattr(self.app, "gsn_modules", []):
            self._remove_module_from_parent(module)
            self.app.gsn_modules.append(module)

    # ------------------------------------------------------------------
    def _is_descendant_module(self, module: GSNModule, potential_parent: GSNModule):
        if module is potential_parent:
            return True
        for sub in module.modules:
            if self._is_descendant_module(sub, potential_parent):
                return True
        return False

    # ------------------------------------------------------------------
    def _on_double_click(self, _event):
        self.open_item()

    # ------------------------------------------------------------------
    def open_item(self):  # pragma: no cover - requires tkinter
        if not self.app:
            return
        sel = self.tree.selection()
        if not sel:
            return
        typ, obj = self.item_map.get(sel[0], (None, None))
        if typ != "diagram":
            return
        if self.app and hasattr(self.app, "open_gsn_diagram"):
            self.app.open_gsn_diagram(obj)
            return
        win = tk.Toplevel(self)
        win.title(obj.root.user_name)
        canvas = tk.Canvas(win, width=800, height=600, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)
        obj.draw(canvas)

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
        else:
            img.put(c, to=(2, 2, size - 2, size - 2))
        return img
