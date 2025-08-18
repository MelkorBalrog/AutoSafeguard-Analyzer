"""Table view showing solutions for a safety & security case."""
from __future__ import annotations

import math
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, simpledialog

from analysis.constants import CHECK_MARK
from analysis.safety_case import SafetyCase
from gui import messagebox
from gui.toolboxes import configure_table_style, _wrap_val


try:  # pragma: no cover - fallback if AutoML isn't fully imported yet
    from AutoML import PMHF_TARGETS  # type: ignore
except Exception:  # pragma: no cover - default targets
    PMHF_TARGETS = {"D": 1e-8, "C": 1e-7, "B": 1e-7, "A": 1e-6, "QM": 1.0}


class SafetyCaseTable(tk.Frame):
    """Display solution nodes of a :class:`SafetyCase` in an interactive table."""

    def __init__(self, master, case: SafetyCase, app=None):
        if isinstance(master, tk.Toplevel):
            container = master
        else:
            container = master
        super().__init__(container)
        self.case = case
        self.app = app
        self._node_lookup = {}
        if isinstance(master, tk.Toplevel):
            master.title(f"Safety Case: {case.name}")
            master.geometry("900x300")
            self.pack(fill=tk.BOTH, expand=True)

        columns = (
            "solution",
            "description",
            "work_product",
            "evidence_link",
            "validation_target",
            "achieved_probability",
            "spi",
            "evidence_ok",
            "notes",
        )
        self.columns = columns
        style_name = "SafetyCase.Treeview"
        try:
            configure_table_style(style_name, rowheight=80)
            self.tree = ttk.Treeview(
                self, columns=columns, show="headings", style=style_name
            )
        except Exception:
            self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.style_name = self.tree.cget("style") or style_name
        headers = {
            "solution": "Solution",
            "description": "Description",
            "work_product": "Work Product",
            "evidence_link": "Evidence Link",
            "validation_target": "Validation Target",
            "achieved_probability": "Achieved Probability",
            "spi": "SPI",
            "evidence_ok": "Evidence OK",
            "notes": "Notes",
        }
        for col in columns:
            self.tree.heading(col, text=headers[col])
            width = 120
            if col in ("description", "evidence_link", "notes"):
                width = 200
            self.tree.column(col, width=width, stretch=True, anchor="center")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Configure>", self._adjust_text)

        self.populate()

    # ------------------------------------------------------------------
    def _parse_spi_target(self, target: str) -> tuple[str, str]:
        if hasattr(self.app, "_parse_spi_target"):
            return self.app._parse_spi_target(target)
        if target.endswith(")") and "(" in target:
            name, typ = target.rsplit(" (", 1)
            return name, typ[:-1]
        return target, ""

    # ------------------------------------------------------------------
    def _product_goal_name(self, sg) -> str:
        if hasattr(self.app, "_product_goal_name"):
            return self.app._product_goal_name(sg)
        return getattr(sg, "user_name", "") or f"SG {getattr(sg, 'unique_id', '')}"

    # ------------------------------------------------------------------
    def populate(self):
        """Fill the table with solution nodes from the case."""
        self.tree.delete(*self.tree.get_children())
        self._node_lookup = {}
        app = getattr(self, "app", None)
        for sol in self.case.solutions:
            self._node_lookup[sol.unique_id] = sol
            v_target = ""
            prob = ""
            spi_val = ""
            if app is not None:
                target = getattr(sol, "spi_target", "")
                if target:
                    pg_name, spi_type = self._parse_spi_target(target)
                    te = None
                    for sg in getattr(app, "top_events", []):
                        if self._product_goal_name(sg) == pg_name:
                            te = sg
                            break
                    if te:
                        if spi_type == "FUSA":
                            p = getattr(te, "probability", "")
                            vt = PMHF_TARGETS.get(getattr(te, "safety_goal_asil", ""), "")
                        else:
                            p = getattr(te, "spi_probability", "")
                            vt = getattr(te, "validation_target", "")
                        p_val = vt_val = None
                        if p not in ("", None):
                            try:
                                p_val = float(p)
                                prob = f"{p_val:.2e}"
                            except Exception:
                                prob = ""
                        if vt not in ("", None):
                            try:
                                vt_val = float(vt)
                                v_target = f"{vt_val:.2e}"
                            except Exception:
                                v_target = ""
                        try:
                            if vt_val not in (None, 0) and p_val not in (None, 0):
                                spi_val = f"{math.log10(vt_val / p_val):.2f}"
                        except Exception:
                            spi_val = ""
            self.tree.insert(
                "",
                "end",
                values=(
                    _wrap_val(sol.user_name),
                    _wrap_val(getattr(sol, "description", ""), 40),
                    _wrap_val(getattr(sol, "work_product", "")),
                    _wrap_val(getattr(sol, "evidence_link", ""), 40),
                    _wrap_val(v_target),
                    _wrap_val(prob),
                    _wrap_val(spi_val),
                    _wrap_val(
                        CHECK_MARK if getattr(sol, "evidence_sufficient", False) else ""
                    ),
                    _wrap_val(getattr(sol, "manager_notes", ""), 40),
                ),
                tags=(sol.unique_id,),
            )
        self._adjust_text()

    # ------------------------------------------------------------------
    def _adjust_text(self, event=None):
        """Re-wrap cell text based on current column widths."""
        if getattr(self, "_adjusting", False):
            return
        self._adjusting = True
        try:
            if not hasattr(self.tree, "column"):
                return
            try:
                font = tkfont.nametofont("TkDefaultFont")
            except Exception:
                return
            char_w = font.measure("0") or 1
            max_lines = 1
            for col in self.columns:
                width = self.tree.column(col, width=None)
                if width <= 0:
                    continue
                wrap = max(int(width / char_w), 1)
                for item in self.tree.get_children():
                    raw = self.tree.set(item, col).replace("\n", " ")
                    wrapped = _wrap_val(raw, wrap)
                    self.tree.set(item, col, wrapped)
                    lines = wrapped.count("\n") + 1
                    if lines > max_lines:
                        max_lines = lines
            style = ttk.Style()
            line_h = font.metrics("linespace")
            style.configure(self.style_name, rowheight=max(line_h * max_lines, 20))
        finally:
            self._adjusting = False
    # ------------------------------------------------------------------
    def _on_double_click(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row or not col:
            return
        idx = int(col[1:]) - 1
        col_name = self.columns[idx]
        tags = self.tree.item(row, "tags")
        if not tags:
            return
        uid = tags[0]
        node = self._node_lookup.get(uid)
        if not node:
            return
        if col_name == "evidence_ok":
            current = self.tree.set(row, "evidence_ok")
            new_val = "" if current == CHECK_MARK else CHECK_MARK
            if messagebox.askokcancel("Evidence", "Are you sure?"):
                if self.app and hasattr(self.app, "push_undo_state"):
                    self.app.push_undo_state()
                node.evidence_sufficient = new_val == CHECK_MARK
                self.tree.set(row, "evidence_ok", new_val)
        elif col_name == "achieved_probability" and getattr(self, "app", None) is not None:
            target = getattr(node, "spi_target", "")
            pg_name, spi_type = self._parse_spi_target(target)
            te = None
            for sg in getattr(self.app, "top_events", []):
                if self._product_goal_name(sg) == pg_name:
                    te = sg
                    break
            if te:
                attr = "probability" if spi_type == "FUSA" else "spi_probability"
                new_val = simpledialog.askfloat(
                    "Achieved Probability",
                    "Enter achieved probability:",
                    initialvalue=getattr(te, attr, 0.0),
                )
                if new_val is not None:
                    if self.app and hasattr(self.app, "push_undo_state"):
                        self.app.push_undo_state()
                    setattr(te, attr, float(new_val))
                    self.populate()
                    if hasattr(self.app, "refresh_safety_performance_indicators"):
                        self.app.refresh_safety_performance_indicators()
                    if hasattr(self.app, "update_views"):
                        self.app.update_views()
        elif col_name == "notes":
            current = self.tree.set(row, "notes")
            new_val = simpledialog.askstring(
                "Notes", "Enter notes:", initialvalue=current
            )
            if new_val is not None:
                if self.app and hasattr(self.app, "push_undo_state"):
                    self.app.push_undo_state()
                node.manager_notes = new_val
                self.tree.set(row, "notes", new_val)
