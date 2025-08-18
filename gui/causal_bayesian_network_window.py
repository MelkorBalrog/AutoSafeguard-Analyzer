import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, simpledialog
from itertools import product
import re

from analysis.causal_bayesian_network import CausalBayesianNetworkDoc
from gui import messagebox
from gui.tooltip import ToolTip
from gui.drawing_helper import FTADrawingHelper
from gui.style_manager import StyleManager


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
            "Variable",
            "Triggering Condition",
            "Existing Triggering Condition",
            "Functional Insufficiency",
            "Existing Functional Insufficiency",
            "Existing Malfunction",
            "Relationship",
        ):
            ttk.Button(toolbox, text=name, command=lambda t=name: self.select_tool(t)).pack(
                fill=tk.X, padx=2, pady=2
            )
        self.current_tool = "Select"

        canvas_container = ttk.Frame(body)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(
            canvas_container,
            background=StyleManager.get_instance().canvas_bg,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        xbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        xbar.grid(row=1, column=0, sticky="ew")
        ybar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        ybar.grid(row=0, column=1, sticky="ns")
        canvas_container.rowconfigure(0, weight=1)
        canvas_container.columnconfigure(0, weight=1)
        self.canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-1>", self.on_double_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
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

        self.zoom_level = 1.0
        self.base_radius = self.NODE_RADIUS
        self.base_font_size = 10
        self.text_font = tkfont.Font(size=self.base_font_size)

        self.refresh_docs()
        self.pack(fill=tk.BOTH, expand=True)
        self._bind_shortcuts()
        self.focus_set()

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
    def redraw(self):
        self.canvas.configure(background=StyleManager.get_instance().canvas_bg)
        self.select_doc()

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

        configure = getattr(self.canvas, "configure", None)
        if configure:
            node_tools = {
                "Variable",
                "Triggering Condition",
                "Existing Triggering Condition",
                "Functional Insufficiency",
                "Existing Functional Insufficiency",
                "Existing Malfunction",
            }
            if tool == "Relationship":
                configure(cursor="tcross")
            elif tool in node_tools:
                configure(cursor="crosshair")
            else:
                configure(cursor="")

    # ------------------------------------------------------------------
    def on_click(self, event) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        if self.current_tool == "Variable":
            undo = getattr(self.app, "push_undo_state", None)
            if undo:
                undo()
            name = simpledialog.askstring("Variable", "Name:", parent=self)
            if not name or name in doc.network.nodes:
                self.select_tool("Select")
                return
            x, y = event.x, event.y
            doc.network.add_node(name, cpd=0.5)
            doc.positions[name] = (x, y)
            doc.types[name] = "variable"
            self._draw_node(name, x, y, "variable")
            self.select_tool("Select")
        elif self.current_tool in ("Triggering Condition", "Functional Insufficiency"):
            prompt = self.current_tool
            name = simpledialog.askstring(prompt, "Name:", parent=self)
            if not name or name in doc.network.nodes:
                self.select_tool("Select")
                return
            undo = getattr(self.app, "push_undo_state", None)
            if undo:
                undo()
            x, y = event.x, event.y
            doc.network.add_node(name, cpd=0.5)
            doc.positions[name] = (x, y)
            kind = "trigger" if self.current_tool == "Triggering Condition" else "insufficiency"
            doc.types[name] = kind
            self._draw_node(name, x, y, kind)
            if kind == "trigger" and hasattr(self.app, "update_triggering_condition_list"):
                self.app.update_triggering_condition_list()
            elif kind == "insufficiency" and hasattr(
                self.app, "update_functional_insufficiency_list"
            ):
                self.app.update_functional_insufficiency_list()
            self.select_tool("Select")
        elif self.current_tool == "Existing Triggering Condition":
            names = self._select_triggering_conditions()
            if not names:
                self.select_tool("Select")
                return
            undo = getattr(self.app, "push_undo_state", None)
            if undo:
                undo()
            x, y = event.x, event.y
            for idx, name in enumerate(names):
                if name in doc.network.nodes:
                    continue
                nx = x + idx * (2 * self.NODE_RADIUS + 10)
                doc.network.add_node(name, cpd=0.5)
                doc.positions[name] = (nx, y)
                doc.types[name] = "trigger"
                self._draw_node(name, nx, y, "trigger")
            if hasattr(self.app, "update_triggering_condition_list"):
                self.app.update_triggering_condition_list()
            self.select_tool("Select")
        elif self.current_tool == "Existing Functional Insufficiency":
            names = self._select_functional_insufficiencies()
            if not names:
                self.select_tool("Select")
                return
            undo = getattr(self.app, "push_undo_state", None)
            if undo:
                undo()
            x, y = event.x, event.y
            for idx, name in enumerate(names):
                if name in doc.network.nodes:
                    continue
                nx = x + idx * (2 * self.NODE_RADIUS + 10)
                doc.network.add_node(name, cpd=0.5)
                doc.positions[name] = (nx, y)
                doc.types[name] = "insufficiency"
                self._draw_node(name, nx, y, "insufficiency")
            if hasattr(self.app, "update_functional_insufficiency_list"):
                self.app.update_functional_insufficiency_list()
        elif self.current_tool == "Existing Malfunction":
            names = self._select_malfunctions()
            if not names:
                return
            undo = getattr(self.app, "push_undo_state", None)
            if undo:
                undo()
            x, y = event.x, event.y
            for idx, name in enumerate(names):
                if name in doc.network.nodes:
                    continue
                nx = x + idx * (2 * self.NODE_RADIUS + 10)
                doc.network.add_node(name, cpd=0.5)
                doc.positions[name] = (nx, y)
                doc.types[name] = "malfunction"
                self._draw_node(name, nx, y, "malfunction")
        elif self.current_tool == "Relationship":
            name = self._find_node(event.x, event.y)
            if not name:
                self.select_tool("Select")
                return
            self.edge_start = name
            self._highlight_node(None)
        else:  # Select tool
            name = self._find_node(event.x, event.y)
            if name:
                undo = getattr(self.app, "push_undo_state", None)
                if undo:
                    undo()
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
            dx, dy = x - old_x, y - old_y
            doc.positions[name] = (x, y)
            oval_id, text_id, fill_tag = self.nodes[name]
            r = self.NODE_RADIUS
            # Move the gradient fill, node outline and label together
            self.canvas.move(fill_tag, dx, dy)
            self.canvas.move(oval_id, dx, dy)
            self.canvas.move(text_id, dx, dy)
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
            self._update_scroll_region()
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
            self._update_scroll_region()

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
                kind_src = doc.types.get(src)
                kind_dst = doc.types.get(dst)
                if kind_src == "insufficiency" and kind_dst == "trigger":
                    messagebox.showerror(
                        "Invalid Relationship",
                        "Functional insufficiency cannot connect to a triggering condition.",
                        parent=self,
                    )
                elif kind_src == "malfunction":
                    messagebox.showerror(
                        "Invalid Relationship",
                        "Malfunction nodes cannot connect to other nodes.",
                        parent=self,
                    )
                else:
                    undo = getattr(self.app, "push_undo_state", None)
                    if undo:
                        undo()
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
            self.select_tool("Select")

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
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
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
            stereo = "triggering condition"
        elif kind == "insufficiency":
            color = "lightyellow"
            stereo = "functional insufficiency"
        elif kind == "malfunction":
            color = "lightgreen"
            stereo = "malfunction"
        elif kind == "variable":
            color = "lightgray"
            stereo = "variable"
        else:
            color = "lightyellow"
            stereo = None
        safe_name = re.sub(r"\W", "_", name)
        fill_tag = f"fill_{safe_name}"
        fill_ids = self.drawing_helper._fill_gradient_circle(
            self.canvas, x, y, r, color, tag=fill_tag
        ) or []
        oval = self.canvas.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            outline=StyleManager.get_instance().outline_color,
            fill="",
        )
        label = f"<<{stereo}>>\n{name}" if stereo else name
        font = getattr(self, "text_font", None)
        if font:
            text = self.canvas.create_text(x, y, text=label, font=font)
        else:
            text = self.canvas.create_text(x, y, text=label)
        self.nodes[name] = (oval, text, fill_tag)
        self.id_to_node[oval] = name
        self.id_to_node[text] = name
        for fid in fill_ids:
            self.id_to_node[fid] = name
        self._place_table(name)
        self._update_scroll_region()

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
        self._update_scroll_region()

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
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH)
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=0)
        for c in cols:
            tree.heading(c, text=c)
            is_prob = c == prob_col or (parents and c == joint_col)
            tree.column(c, width=80 if is_prob else 60, anchor=tk.CENTER)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.columnconfigure(0, weight=1)
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
        self._update_scroll_region()

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
            for combo, prob, combo_prob, joint in rows:
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
    def _update_all_tables(self) -> None:
        """Update probability tables for all nodes in the active document."""
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        for node in doc.network.nodes:
            if node in self.tables:
                self._update_table(node)

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
                undo = getattr(self.app, "push_undo_state", None)
                if undo:
                    undo()
                doc.network.cpds[name] = prob
                self._update_all_tables()
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
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
        doc.network.cpds.setdefault(name, {})[tuple(values)] = prob
        self._update_all_tables()

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
                undo = getattr(self.app, "push_undo_state", None)
                if undo:
                    undo()
                doc.network.cpds[name] = prob
                self._update_all_tables()
            return
        current = tuple(v == "T" for v in values[:-1])
        prob = simpledialog.askfloat(
            "Probability", f"P({name}=True)", minvalue=0.0, maxvalue=1.0, parent=self
        )
        if prob is None:
            return
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
        doc.network.cpds[name][current] = prob
        self._update_all_tables()

    # ------------------------------------------------------------------
    def _select_triggering_conditions(self) -> list[str]:
        """Return existing triggering conditions chosen by the user."""
        tcs = sorted(getattr(self.app, "triggering_conditions", []))
        if not tcs:
            messagebox.showinfo(
                "No Triggering Conditions",
                "No triggering conditions available.",
                parent=self,
            )
            return []
        prompt = ", ".join(tcs)
        sel = simpledialog.askstring(
            "Existing Triggering Conditions",
            f"Names (comma separated):\n{prompt}",
            parent=self,
        )
        if not sel:
            return []
        return [n.strip() for n in sel.split(",") if n.strip() in tcs]

    # ------------------------------------------------------------------
    def _select_functional_insufficiencies(self) -> list[str]:
        """Return existing functional insufficiencies chosen by the user."""
        fis = sorted(getattr(self.app, "functional_insufficiencies", []))
        if not fis:
            messagebox.showinfo(
                "No Functional Insufficiencies",
                "No functional insufficiencies available.",
                parent=self,
            )
            return []
        prompt = ", ".join(fis)
        sel = simpledialog.askstring(
            "Existing Functional Insufficiencies",
            f"Names (comma separated):\n{prompt}",
            parent=self,
        )
        if not sel:
            return []
        return [n.strip() for n in sel.split(",") if n.strip() in fis]

    # ------------------------------------------------------------------
    def _select_malfunctions(self) -> list[str]:
        """Return a list of existing malfunctions chosen by the user."""
        mals = sorted(getattr(self.app, "malfunctions", []))
        if not mals:
            messagebox.showinfo("No Malfunctions", "No malfunctions available.", parent=self)
            return []
        prompt = ", ".join(mals)
        sel = simpledialog.askstring(
            "Existing Malfunctions",
            f"Names (comma separated):\n{prompt}",
            parent=self,
        )
        if not sel:
            return []
        return [n.strip() for n in sel.split(",") if n.strip() in mals]

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
        self._update_scroll_region()

    # ------------------------------------------------------------------
    def refresh_from_repository(self, _event=None) -> None:
        """Refresh the canvas after undo/redo operations."""
        self.refresh_docs()

    # ------------------------------------------------------------------
    def _update_scroll_region(self) -> None:
        if not hasattr(self.canvas, "bbox") or not hasattr(self.canvas, "configure"):
            return
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

    # ------------------------------------------------------------------
    def _bind_shortcuts(self) -> None:
        if self.app:
            self.bind("<Control-z>", lambda e: self.app.undo())
            self.bind("<Control-y>", lambda e: self.app.redo())
            self.bind("<Control-plus>", lambda e: self.zoom(1.1))
            self.bind("<Control-minus>", lambda e: self.zoom(0.9))
            self.bind("<Control-=>", lambda e: self.zoom(1.1))

    # ------------------------------------------------------------------
    def zoom(self, factor: float) -> None:
        self.zoom_level *= factor
        self.NODE_RADIUS = self.base_radius * self.zoom_level
        self.canvas.scale("all", 0, 0, factor, factor)
        doc = getattr(self.app, "active_cbn", None)
        if doc:
            for name, (x, y) in doc.positions.items():
                doc.positions[name] = (x * factor, y * factor)
        if hasattr(self, "text_font"):
            self.text_font.configure(size=int(self.base_font_size * self.zoom_level))
        self._update_scroll_region()

    # ------------------------------------------------------------------
    def on_right_click(self, event) -> None:  # pragma: no cover - requires tkinter
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        name = self._find_node(event.x, event.y)
        if not name:
            return
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Rename", command=lambda n=name: self._prompt_rename_node(n))
        menu.add_command(label="Delete", command=lambda n=name: self._delete_node(n))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:  # pragma: no cover - no-op on simple stubs
            grab = getattr(menu, "grab_release", None)
            if grab:
                grab()

    # ------------------------------------------------------------------
    def _prompt_rename_node(self, name: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        new = simpledialog.askstring("Edit Node", "Name:", initialvalue=name, parent=self)
        if not new or new == name:
            return
        if new in doc.network.nodes:
            messagebox.showerror("Edit Node", "Name already exists", parent=self)
            return
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
        self._rename_node(name, new)
        self._update_all_tables()

    # ------------------------------------------------------------------
    def _delete_node(self, name: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        delete_model = messagebox.askyesno(
            "Delete Node",
            "Delete node from model?\nNo removes it from diagram only.",
            parent=self,
        )
        undo = getattr(self.app, "push_undo_state", None)
        if undo:
            undo()
        if delete_model:
            if name in doc.network.nodes:
                doc.network.nodes.remove(name)
            doc.network.cpds.pop(name, None)
            doc.network.parents.pop(name, None)
            for child, parents in list(doc.network.parents.items()):
                if name in parents:
                    parents.remove(name)
                    doc.network.cpds[child] = {}
                    self._rebuild_table(child)
        oval_text = self.nodes.pop(name, None)
        if oval_text:
            oval_id, text_id, fill_tag = oval_text
            self.canvas.delete(oval_id)
            self.canvas.delete(text_id)
            find_withtag = getattr(self.canvas, "find_withtag", None)
            if find_withtag:
                for fid in find_withtag(fill_tag):
                    self.canvas.delete(fid)
                    self.id_to_node.pop(fid, None)
            self.id_to_node.pop(oval_id, None)
            self.id_to_node.pop(text_id, None)
        if name in self.tables:
            win, _, _ = self.tables.pop(name)
            self.canvas.delete(win)
        doc.positions.pop(name, None)
        doc.types.pop(name, None)
        if self.selected_node == name:
            self._highlight_node(None)
        for line, src, dst in self.edges[:]:
            if src == name or dst == name:
                self.canvas.delete(line)
                self.edges.remove((line, src, dst))
        self._update_scroll_region()

    # ------------------------------------------------------------------
    def _rename_node(self, old: str, new: str) -> None:
        doc = getattr(self.app, "active_cbn", None)
        if not doc:
            return
        doc.network.nodes = [new if n == old else n for n in doc.network.nodes]
        doc.network.cpds[new] = doc.network.cpds.pop(old)
        if old in doc.network.parents:
            doc.network.parents[new] = doc.network.parents.pop(old)
        for child, parents in doc.network.parents.items():
            doc.network.parents[child] = [new if p == old else p for p in parents]
        doc.positions[new] = doc.positions.pop(old)
        doc.types[new] = doc.types.pop(old)
        oval_id, text_id, old_fill_tag = self.nodes.pop(old)
        safe_new = re.sub(r"\W", "_", new)
        new_fill_tag = f"fill_{safe_new}"
        self.nodes[new] = (oval_id, text_id, new_fill_tag)
        self.id_to_node[oval_id] = new
        self.id_to_node[text_id] = new
        find_withtag = getattr(self.canvas, "find_withtag", None)
        if find_withtag:
            for fid in find_withtag(old_fill_tag):
                self.canvas.itemconfigure(fid, tags=(new_fill_tag,))
                self.id_to_node[fid] = new
        kind = doc.types.get(new)
        if kind == "trigger":
            stereo = "triggering condition"
        elif kind == "insufficiency":
            stereo = "functional insufficiency"
        elif kind == "malfunction":
            stereo = "malfunction"
        elif kind == "variable":
            stereo = "variable"
        else:
            stereo = None
        label = f"<<{stereo}>>\n{new}" if stereo else new
        if hasattr(self, "text_font"):
            self.canvas.itemconfigure(text_id, text=label, font=self.text_font)
        else:
            self.canvas.itemconfigure(text_id, text=label)
        for idx, (line, src, dst) in enumerate(self.edges):
            s = new if src == old else src
            d = new if dst == old else dst
            self.edges[idx] = (line, s, d)
        self._rebuild_table(new)
        for child, parents in doc.network.parents.items():
            if new in parents and child != new:
                self._rebuild_table(child)

