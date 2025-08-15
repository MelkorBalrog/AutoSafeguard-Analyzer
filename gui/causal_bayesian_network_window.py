import tkinter as tk
from tkinter import ttk, simpledialog
from itertools import product

from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from gui import messagebox
from gui.tooltip import ToolTip
from gui.drawing_helper import FTADrawingHelper


class CausalBayesianNetworkWindow(tk.Frame):
    """Editor for Causal Bayesian Network analyses with diagram support."""

    NODE_RADIUS = 30

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("Causal Bayesian Network Analysis")

        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Analysis:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        toolbox = ttk.Frame(body)
        toolbox.pack(side=tk.LEFT, fill=tk.Y)
        for name in (
            "Select",
            "Triggering Condition",
            "Functional Insufficiency",
            "Relationship",
        ):
            ttk.Button(toolbox, text=name, command=lambda t=name: self.select_tool(t)).pack(
                fill=tk.X, padx=2, pady=2
            )
        self.current_tool = "Select"

        self.canvas = tk.Canvas(body, background="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-1>", self.on_double_click)
        self.drawing_helper = FTADrawingHelper()

        self.nodes = {}  # name -> (oval_id, text_id, fill_tag)
        self.tables = {}  # name -> (window_id, frame, treeview)
        self.id_to_node = {}
        self.edges = []  # (line_id, src, dst)
        self.edge_start = None
        self.drag_node = None
        self.selected_node = None
        self.selection_rect = None
        self.temp_edge_line = None
        self.temp_edge_anim = None
        self.temp_edge_offset = 0

        self.refresh_docs()
        self.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    def refresh_docs(self) -> None:
        names = [doc.name for doc in getattr(self.app, "cbn_docs", [])]
        self.doc_cb.configure(values=names)
        if names:
            current = self.doc_var.get()
            if current not in names:
                self.doc_var.set(names[0])
            self.select_doc()
        else:
            self.doc_var.set("")
            self.app.active_cbn = None
            self.canvas.delete("all")

    # ------------------------------------------------------------------
    def select_doc(self, *_):
        name = self.doc_var.get()
        for doc in getattr(self.app, "cbn_docs", []):
            if doc.name == name:
                self.app.active_cbn = doc
                break
        else:
            self.app.active_cbn = None
        self.load_doc()

    # ------------------------------------------------------------------
    def new_doc(self) -> None:
        name = simpledialog.askstring("New Analysis", "Name:", parent=self)
        if not name:
            return
        doc = CausalBayesianNetworkDoc(name)
        if not hasattr(self.app, "cbn_docs"):
            self.app.cbn_docs = []
        self.app.cbn_docs.append(doc)
        toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
        if toolbox:
            toolbox.register_created_work_product("Causal Bayesian Network Analysis", name)
        self.refresh_docs()
        self.doc_var.set(name)
        self.select_doc()

    # ------------------------------------------------------------------
    def rename_doc(self) -> None:
        old = self.doc_var.get()
        if not old:
            return
        new = simpledialog.askstring("Rename Analysis", "Name:", initialvalue=old, parent=self)
        if not new or new == old:
            return
        for doc in getattr(self.app, "cbn_docs", []):
            if doc.name == old:
                doc.name = new
                toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
                if toolbox:
                    toolbox.rename_document("Causal Bayesian Network Analysis", old, new)
                break
        self.refresh_docs()
        self.doc_var.set(new)

    # ------------------------------------------------------------------
    def delete_doc(self) -> None:
        name = self.doc_var.get()
        if not name:
            return
        docs = getattr(self.app, "cbn_docs", [])
        for idx, doc in enumerate(docs):
            if doc.name == name:
                del docs[idx]
                toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
                if toolbox:
                    toolbox.register_deleted_work_product("Causal Bayesian Network Analysis", name)
                break
        self.refresh_docs()

    # ------------------------------------------------------------------
    def select_tool(self, tool: str) -> None:
        self.current_tool = tool
        self.edge_start = None
        self.drag_node = None
        if tool != "Select":
            self._highlight_node(None)

    # ------------------------------------------------------------------
    def on_click(self, event) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        if self.current_tool in ("Triggering Condition", "Functional Insufficiency"):
            prompt = self.current_tool
            name = simpledialog.askstring(prompt, "Name:", parent=self)
            if not name or name in doc.network.nodes:
                return
            x, y = event.x, event.y
            doc.network.add_node(name, cpd=0.5)
            doc.positions[name] = (x, y)
            kind = "trigger" if self.current_tool == "Triggering Condition" else "insufficiency"
            doc.types[name] = kind
            self._draw_node(name, x, y, kind)
        elif self.current_tool == "Relationship":
            name = self._find_node(event.x, event.y)
            if not name:
                return
            self.edge_start = name
            self._highlight_node(None)
        else:  # Select tool
            name = self._find_node(event.x, event.y)
            self.drag_node = name
            self.drag_offset = (0, 0)
            self._highlight_node(name)
            if name:
                x, y = doc.positions.get(name, (0, 0))
                self.drag_offset = (x - event.x, y - event.y)

    # ------------------------------------------------------------------
    def on_drag(self, event) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        if self.current_tool == "Select" and self.drag_node:
            name = self.drag_node
            old_x, old_y = doc.positions.get(name, (0, 0))
            x, y = event.x + self.drag_offset[0], event.y + self.drag_offset[1]
            doc.positions[name] = (x, y)
            oval_id, text_id, fill_tag = self.nodes[name]
            r = self.NODE_RADIUS
            self.canvas.coords(fill_tag, x - r, y - r, x + r, y + r)
            self.canvas.coords(oval_id, x - r, y - r, x + r, y + r)
            self.canvas.coords(text_id, x, y)
            self.canvas.move(fill_tag, x - old_x, y - old_y)
            for line_id, src, dst in self.edges:
                if src == name or dst == name:
                    x1, y1 = doc.positions[src]
                    x2, y2 = doc.positions[dst]
                    dx, dy = x2 - x1, y2 - y1
                    dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
                    sx = x1 + dx / dist * r
                    sy = y1 + dy / dist * r
                    tx = x2 - dx / dist * r
                    ty = y2 - dy / dist * r
                    self.canvas.coords(line_id, sx, sy, tx, ty)
            self._position_table(name, x, y)
            if self.selected_node == name and self.selection_rect:
                self.canvas.coords(self.selection_rect, x - r, y - r, x + r, y + r)
        elif self.current_tool == "Relationship" and self.edge_start:
            x1, y1 = doc.positions.get(self.edge_start, (0, 0))
            if self.temp_edge_line is None:
                self.temp_edge_line = self.canvas.create_line(
                    x1, y1, event.x, event.y, dash=(2, 2)
                )
                self.temp_edge_offset = 0
                self._animate_temp_edge()
            else:
                self.canvas.coords(self.temp_edge_line, x1, y1, event.x, event.y)

    # ------------------------------------------------------------------
    def on_release(self, event) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        if self.current_tool == "Select":
            self.drag_node = None
        elif self.current_tool == "Relationship" and self.edge_start:
            dst = self._find_node(event.x, event.y)
            src = self.edge_start
            if dst and dst != src:
                self._draw_edge(src, dst)
                parents = doc.network.parents.setdefault(dst, [])
                if src not in parents:
                    parents.append(src)
                    doc.network.cpds[dst] = {}
                    self._rebuild_table(dst)
            self.edge_start = None
            if self.temp_edge_line:
                self.canvas.delete(self.temp_edge_line)
                self.temp_edge_line = None
            if self.temp_edge_anim:
                self.after_cancel(self.temp_edge_anim)
                self.temp_edge_anim = None

    # ------------------------------------------------------------------
    def _animate_temp_edge(self):
        if self.temp_edge_line:
            self.temp_edge_offset = (self.temp_edge_offset + 2) % 12
            self.canvas.itemconfigure(
                self.temp_edge_line, dashoffset=self.temp_edge_offset
            )
            self.temp_edge_anim = self.after(100, self._animate_temp_edge)

    # ------------------------------------------------------------------
    def _highlight_node(self, name: str | None) -> None:
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
        self.selected_node = name
        if not name:
            return
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        x, y = doc.positions.get(name, (0, 0))
        r = self.NODE_RADIUS
        self.selection_rect = self.canvas.create_rectangle(
            x - r, y - r, x + r, y + r, outline="red", dash=(2, 2)
        )

    # ------------------------------------------------------------------
    def on_double_click(self, event) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        name = self._find_node(event.x, event.y)
        if not name:
            return
        parents = doc.network.parents.get(name, [])
        if not parents:
            prob = simpledialog.askfloat(
                "Prior",
                f"P({name}=True)",
                minvalue=0.0,
                maxvalue=1.0,
                parent=self,
            )
            if prob is not None:
                doc.network.cpds[name] = prob
                self._update_all_tables()
            return
        cpds = {}
        for combo in product([True, False], repeat=len(parents)):
            label = ", ".join(
                f"{p}={'T' if val else 'F'}" for p, val in zip(parents, combo)
            )
            prob = simpledialog.askfloat(
                "CPD",
                f"P({name}=True | {label})",
                minvalue=0.0,
                maxvalue=1.0,
                parent=self,
            )
            if prob is None:
                return
            cpds[combo] = prob
        doc.network.cpds[name] = cpds
        self._update_all_tables()

    # ------------------------------------------------------------------
    def _draw_node(self, name: str, x: float, y: float, kind: str | None = None) -> None:
        """Draw a node as a filled circle with a text label."""
        r = self.NODE_RADIUS
        if kind == "trigger":
            color = "lightblue"
        elif kind == "insufficiency":
            color = "lightyellow"
        else:
            color = "lightyellow"
        fill_tag = f"fill_{name}"
        self.drawing_helper._fill_gradient_circle(self.canvas, x, y, r, color, tag=fill_tag)
        oval = self.canvas.create_oval(
            x - r, y - r, x + r, y + r, outline="black", fill=""
        )
        text = self.canvas.create_text(x, y, text=name)
        self.nodes[name] = (oval, text, fill_tag)
        self.id_to_node[oval] = name
        self.id_to_node[text] = name
        self._place_table(name)

    # ------------------------------------------------------------------
    def _draw_edge(self, src: str, dst: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        x1, y1 = doc.positions.get(src, (0, 0))
        x2, y2 = doc.positions.get(dst, (0, 0))
        r = self.NODE_RADIUS
        dx, dy = x2 - x1, y2 - y1
        dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
        sx = x1 + dx / dist * r
        sy = y1 + dy / dist * r
        tx = x2 - dx / dist * r
        ty = y2 - dy / dist * r
        line = self.canvas.create_line(sx, sy, tx, ty, arrow=tk.LAST)
        self.edges.append((line, src, dst))

    # ------------------------------------------------------------------
    def _place_table(self, name: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        parents = doc.network.parents.get(name, [])
        prob_col = f"P({name}=T)"
        if parents:
            joint_col = f"P({name}=T, parents)"
            cols = list(parents) + [joint_col]
        else:
            cols = [prob_col]
        frame = ttk.Frame(self.canvas)
        label_text = (
            f"Prior probability of {name}" if not parents else f"Conditional probabilities for {name}"
        )
        label = ttk.Label(frame, text=label_text)
        label.pack(side=tk.TOP, fill=tk.X)
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=0)
        for c in cols:
            tree.heading(c, text=c)
            is_prob = c == prob_col or (parents and c == joint_col)
            tree.column(c, width=80 if is_prob else 60, anchor=tk.CENTER)
        tree.pack(side=tk.TOP, fill=tk.X)
        if not parents:
            info = f"Prior probability that {name} is True"
        else:
            info = (
                "Each row shows a combination of parent values; "
                f"{joint_col} is the joint probability that the parents take that combination "
                f"and {name} is True"
            )
        ToolTip(tree, info)
        tree.bind("<Double-1>", lambda e, n=name: self.edit_cpd_row(n))
        win = self.canvas.create_window(0, 0, window=frame, anchor="nw")
        self.tables[name] = (win, frame, tree)
        self._update_table(name)
        x, y = doc.positions.get(name, (0, 0))
        self._position_table(name, x, y)

    # ------------------------------------------------------------------
    def _update_table(self, name: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc or name not in self.tables:
            return
        win, frame, tree = self.tables[name]
        tree.delete(*tree.get_children())
        parents = doc.network.parents.get(name, [])
        rows = doc.network.cpd_rows(name)
        if not parents:
            tree.insert("", "end", values=[f"{rows[0][1]:.3f}"])
        else:
            for combo, prob, combo_prob in rows:
                joint = combo_prob * prob
                row = ["T" if val else "F" for val in combo]
                row.append(f"{joint:.3f}")
                tree.insert("", "end", values=row)
        tree.configure(height=len(rows))
        frame.update_idletasks()
        self.canvas.itemconfigure(
            win, width=frame.winfo_reqwidth(), height=frame.winfo_reqheight()
        )
        x, y = doc.positions.get(name, (0, 0))
        self._position_table(name, x, y)

    # ------------------------------------------------------------------
    def _position_table(self, name: str, x: float, y: float) -> None:
        if name not in self.tables:
            return
        win, frame, _ = self.tables[name]
        frame.update_idletasks()
        w, h = frame.winfo_reqwidth(), frame.winfo_reqheight()
        r = self.NODE_RADIUS
        self.canvas.itemconfigure(win, width=w, height=h)
        self.canvas.coords(win, x + r + 10, y - h / 2)

    # ------------------------------------------------------------------
    def _update_all_tables(self) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        for node in doc.network.nodes:
            self._update_table(node)

    # ------------------------------------------------------------------
    def _rebuild_table(self, name: str) -> None:
        if name in self.tables:
            win, frame, _ = self.tables.pop(name)
            self.canvas.delete(win)
            frame.destroy()
        self._place_table(name)

    # ------------------------------------------------------------------
    def edit_cpd_row(self, name: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc or name not in self.tables:
            return
        parents = doc.network.parents.get(name, [])
        _, _, tree = self.tables[name]
        item = tree.focus()
        if not item:
            return
        values = tree.item(item, "values")
        if not parents:
            prob = simpledialog.askfloat(
                "Prior", f"P({name}=True)", minvalue=0.0, maxvalue=1.0, parent=self
            )
            if prob is not None:
                doc.network.cpds[name] = prob
                self._update_all_tables()
            return
        current = tuple(v == "T" for v in values[:-1])
        prob = simpledialog.askfloat(
            "Probability", f"P({name}=True)", minvalue=0.0, maxvalue=1.0, parent=self
        )
        if prob is None:
            return
        doc.network.cpds[name][current] = prob
        self._update_all_tables()

    # ------------------------------------------------------------------
    def _find_node(self, x: float, y: float) -> str | None:
        ids = self.canvas.find_overlapping(x, y, x, y)
        for i in ids:
            name = self.id_to_node.get(i)
            if name:
                return name
        return None

    # ------------------------------------------------------------------
    def load_doc(self) -> None:
        self.canvas.delete("all")
        self.nodes.clear()
        for _, frame, _ in self.tables.values():
            frame.destroy()
        self.tables.clear()
        self.id_to_node.clear()
        self.edges.clear()
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        for name in doc.network.nodes:
            x, y = doc.positions.get(name, (100, 100))
            doc.positions[name] = (x, y)
            kind = doc.types.get(name)
            self._draw_node(name, x, y, kind)
        for child, parents in doc.network.parents.items():
            for parent in parents:
                if parent in doc.network.nodes and child in doc.network.nodes:
                    self._draw_edge(parent, child)

