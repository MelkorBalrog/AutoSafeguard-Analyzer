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
        for name in ("Select", "Variable", "Relationship"):
            ttk.Button(toolbox, text=name, command=lambda t=name: self.select_tool(t)).pack(
                fill=tk.X, padx=2, pady=2
            )
        ttk.Button(toolbox, text="Calculate", command=self.calculate).pack(
            fill=tk.X, padx=2, pady=2
        )
        self.current_tool = "Select"

        self.canvas = tk.Canvas(body, background="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Double-1>", self.on_double_click)
        self.drawing_helper = FTADrawingHelper()

        # Each entry maps a node name to the canvas item IDs that make up the
        # visual representation of the node.  ``fill_id`` is the filled oval
        # background, ``oval_id`` is the outline and ``text_id`` is the label.
        # Keeping the fill as a separate item allows us to move it together
        # with the outline when the node is dragged.
        self.nodes = {}  # name -> (fill_id, oval_id, text_id)
        self.tables = {}  # name -> (window_id, frame, treeview)
        self.id_to_node = {}
        self.edges = []  # (line_id, src, dst)
        self.edge_start = None
        self.drag_node = None

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

    # ------------------------------------------------------------------
    def on_click(self, event) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        if self.current_tool == "Variable":
            name = simpledialog.askstring("Variable", "Name:", parent=self)
            if not name or name in doc.network.nodes:
                return
            x, y = event.x, event.y
            doc.network.add_node(name, cpd=0.5)
            doc.positions[name] = (x, y)
            self._draw_node(name, x, y)
        elif self.current_tool == "Relationship":
            name = self._find_node(event.x, event.y)
            if not name:
                return
            if self.edge_start is None:
                self.edge_start = name
            else:
                src, dst = self.edge_start, name
                if src == dst:
                    self.edge_start = None
                    return
                self._draw_edge(src, dst)
                parents = doc.network.parents.setdefault(dst, [])
                if src not in parents:
                    parents.append(src)
                    doc.network.cpds[dst] = {}
                    self._rebuild_table(dst)
                self.edge_start = None
        else:  # Select tool
            name = self._find_node(event.x, event.y)
            self.drag_node = name
            self.drag_offset = (0, 0)
            if name:
                x, y = doc.positions.get(name, (0, 0))
                self.drag_offset = (x - event.x, y - event.y)

    # ------------------------------------------------------------------
    def on_drag(self, event) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc or not self.drag_node or self.current_tool != "Select":
            return
        name = self.drag_node
        x, y = event.x + self.drag_offset[0], event.y + self.drag_offset[1]
        doc.positions[name] = (x, y)
        fill_id, oval_id, text_id = self.nodes[name]
        r = self.NODE_RADIUS
        self.canvas.coords(fill_id, x - r, y - r, x + r, y + r)
        self.canvas.coords(oval_id, x - r, y - r, x + r, y + r)
        self.canvas.coords(text_id, x, y)
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
                self._update_table(name)
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
        self._update_table(name)

    # ------------------------------------------------------------------
    def _draw_node(self, name: str, x: float, y: float) -> None:
        """Draw a node as a filled circle with a text label."""
        r = self.NODE_RADIUS
        color = "lightyellow"

        # ``create_oval`` with a fill ensures the colored background is a single
        # canvas item that can be moved when the node is dragged.  Previously the
        # gradient fill was drawn using many individual lines which remained in
        # place when a node was moved, leaving the outline without its fill.
        fill = self.canvas.create_oval(
            x - r, y - r, x + r, y + r, outline="", fill=color
        )
        oval = self.canvas.create_oval(
            x - r, y - r, x + r, y + r, outline="black", fill=""
        )
        text = self.canvas.create_text(x, y, text=name)
        self.nodes[name] = (fill, oval, text)
        self.id_to_node[fill] = name
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
        cols = list(parents) + [prob_col]
        frame = ttk.Frame(self.canvas)
        label_text = (
            f"Prior probability of {name}" if not parents else f"Conditional probabilities for {name}"
        )
        label = ttk.Label(frame, text=label_text)
        label.pack(side=tk.TOP, fill=tk.X)
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=0)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=80 if c == prob_col else 60, anchor=tk.CENTER)
        tree.pack(side=tk.TOP, fill=tk.X)
        if not parents:
            info = f"Prior probability that {name} is True"
        else:
            info = (
                "Each row shows a combination of parent values; "
                f"{prob_col} is the probability that {name} is True for that combination"
            )
        ToolTip(tree, info)
        tree.bind("<Double-1>", lambda e, n=name: self.edit_cpd_row(n))
        add_btn = ttk.Button(frame, text="Add", command=lambda n=name: self.add_cpd_row(n))
        add_btn.pack(side=tk.TOP, fill=tk.X)
        ToolTip(add_btn, "Add a new probability entry")
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
        if not parents:
            prob = doc.network.cpds.get(name, 0.0)
            tree.insert("", "end", values=[f"{prob:.3f}"])
            tree.configure(height=1)
        else:
            cpds = doc.network.cpds.get(name, {})
            for combo, prob in cpds.items():
                row = ["T" if val else "F" for val in combo]
                row.append(f"{prob:.3f}")
                tree.insert("", "end", values=row)
            tree.configure(height=len(cpds) or 1)
        # Update geometry based on the new content so the canvas window adapts to
        # the new size.  Using ``frame.update_idletasks`` ensures the frame and
        # its children recalculates their requested size before we query it.
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
    def _rebuild_table(self, name: str) -> None:
        if name in self.tables:
            win, frame, _ = self.tables.pop(name)
            self.canvas.delete(win)
            frame.destroy()
        self._place_table(name)

    # ------------------------------------------------------------------
    def add_cpd_row(self, name: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        parents = doc.network.parents.get(name, [])
        if not parents:
            prob = simpledialog.askfloat(
                "Prior", f"P({name}=True)", minvalue=0.0, maxvalue=1.0, parent=self
            )
            if prob is not None:
                doc.network.cpds[name] = prob
                self._update_table(name)
            return
        values = []
        for p in parents:
            val = simpledialog.askstring(f"{p}", "T/F", parent=self)
            if val is None:
                return
            values.append(val.strip().upper().startswith("T"))
        prob = simpledialog.askfloat(
            "Probability", f"P({name}=True)", minvalue=0.0, maxvalue=1.0, parent=self
        )
        if prob is None:
            return
        doc.network.cpds.setdefault(name, {})[tuple(values)] = prob
        self._update_table(name)

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
                self._update_table(name)
            return
        current = tuple(v == "T" for v in values[:-1])
        prob = simpledialog.askfloat(
            "Probability", f"P({name}=True)", minvalue=0.0, maxvalue=1.0, parent=self
        )
        if prob is None:
            return
        doc.network.cpds[name][current] = prob
        self._update_table(name)

    # ------------------------------------------------------------------
    def calculate(self) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        lines = []
        for name in doc.network.nodes:
            prob = doc.network.query(name)
            lines.append(f"P({name}=True) = {prob:.3f}")
        messagebox.showinfo("Probabilities", "\n".join(lines), parent=self)

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
            self._draw_node(name, x, y)
        for child, parents in doc.network.parents.items():
            for parent in parents:
                if parent in doc.network.nodes and child in doc.network.nodes:
                    self._draw_edge(parent, child)

