# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import tkinter as tk
from tkinter import ttk, simpledialog

from gui import messagebox
from gui.toolboxes import (
    EditableTreeview,
    configure_table_style,
    _RequirementDialog,
    _SelectRequirementsDialog,
    ToolTip,
)
from analysis.models import (
    StpaEntry,
    StpaDoc,
    global_requirements,
    REQUIREMENT_TYPE_OPTIONS,
)
from sysml.sysml_repository import SysMLRepository
from gui.architecture import DiagramConnection, format_control_flow_label


class StpaWindow(tk.Frame):
    COLS = [
        "action",
        "not_providing",
        "providing",
        "incorrect_timing",
        "stopped_too_soon",
        "safety_constraints",
    ]

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("STPA Analysis")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="STPA:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)
        self.diag_lbl = ttk.Label(top, text="")
        self.diag_lbl.pack(side=tk.LEFT, padx=10)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        configure_table_style("Stpa.Treeview", rowheight=80)
        self.tree = EditableTreeview(
            tree_frame,
            columns=self.COLS,
            show="headings",
            style="Stpa.Treeview",
            edit_callback=self.on_cell_edit,
            height=4,
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in self.COLS:
            self.tree.heading(c, text=c.replace("_", " ").title())
            width = 200 if c == "safety_constraints" else 150
            self.tree.column(c, width=width)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text="Add", command=self.add_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Edit", command=self.edit_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Delete", command=self.del_row).pack(side=tk.LEFT, padx=2, pady=2)

        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Document management
    # ------------------------------------------------------------------
    def refresh_docs(self):
        names = [d.name for d in self.app.stpa_docs]
        self.doc_cb.configure(values=names)
        repo = SysMLRepository.get_instance()
        if self.app.active_stpa:
            self.doc_var.set(self.app.active_stpa.name)
            diag = repo.diagrams.get(self.app.active_stpa.diagram)
            self.diag_lbl.config(text=f"Diagram: {diag.name if diag else ''}")
        elif names:
            self.doc_var.set(names[0])
            self.app.active_stpa = self.app.stpa_docs[0]
            self.app.stpa_entries = self.app.active_stpa.entries
            diag = repo.diagrams.get(self.app.active_stpa.diagram)
            self.diag_lbl.config(text=f"Diagram: {diag.name if diag else ''}")

    def select_doc(self, *_):
        name = self.doc_var.get()
        repo = SysMLRepository.get_instance()
        for d in self.app.stpa_docs:
            if d.name == name:
                self.app.active_stpa = d
                self.app.stpa_entries = d.entries
                diag = repo.diagrams.get(d.diagram)
                self.diag_lbl.config(text=f"Diagram: {diag.name if diag else ''}")
                break
        self.refresh()

    class NewStpaDialog(simpledialog.Dialog):
        def __init__(self, parent, app):
            self.app = app
            super().__init__(parent, title="New STPA")

        def body(self, master):
            ttk.Label(master, text="Name").grid(row=0, column=0, sticky="e")
            self.name_var = tk.StringVar()
            name_entry = ttk.Entry(master, textvariable=self.name_var)
            name_entry.grid(row=0, column=1)
            ttk.Label(master, text="Control Flow Diagram").grid(row=1, column=0, sticky="e")
            repo = SysMLRepository.get_instance()
            diags = [
                d.name or d.diag_id
                for d in repo.diagrams.values()
                if d.diag_type == "Control Flow Diagram"
            ]
            self.diag_var = tk.StringVar()
            ttk.Combobox(
                master, textvariable=self.diag_var, values=diags, state="readonly"
            ).grid(row=1, column=1)
            return name_entry

        def apply(self):
            self.result = (self.name_var.get(), self.diag_var.get())

    def new_doc(self):
        dlg = self.NewStpaDialog(self, self.app)
        if not getattr(dlg, "result", None):
            return
        name, diag_name = dlg.result
        repo = SysMLRepository.get_instance()
        diag_id = next(
            (d.diag_id for d in repo.diagrams.values() if (d.name or d.diag_id) == diag_name),
            "",
        )
        doc = StpaDoc(name, diag_id, [])
        self.app.stpa_docs.append(doc)
        self.app.active_stpa = doc
        self.app.stpa_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_stpa:
            return
        name = simpledialog.askstring(
            "Rename STPA", "Name:", initialvalue=self.app.active_stpa.name
        )
        if not name:
            return
        self.app.active_stpa.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_stpa
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete STPA '{doc.name}'?"):
            return
        self.app.stpa_docs.remove(doc)
        if self.app.stpa_docs:
            self.app.active_stpa = self.app.stpa_docs[0]
        else:
            self.app.active_stpa = None
        self.app.stpa_entries = self.app.active_stpa.entries if self.app.active_stpa else []
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    # ------------------------------------------------------------------
    # Row handling
    # ------------------------------------------------------------------
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.stpa_entries:
            reqs = []
            for rid in row.safety_constraints:
                req = global_requirements.get(rid, {})
                text = req.get("text", "")
                reqs.append(f"[{rid}] {text}" if text else rid)
            vals = [
                row.action,
                row.not_providing,
                row.providing,
                row.incorrect_timing,
                row.stopped_too_soon,
                ";".join(reqs),
            ]
            self.tree.insert("", "end", values=vals)

    def _get_actions(self):
        if not self.app.active_stpa:
            return []
        repo = SysMLRepository.get_instance()
        diag = repo.diagrams.get(self.app.active_stpa.diagram)
        if not diag:
            return []
        actions = []
        for conn_data in getattr(diag, "connections", []):
            conn_obj = (
                DiagramConnection(**conn_data)
                if isinstance(conn_data, dict)
                else conn_data
            )
            if getattr(conn_obj, "conn_type", "") == "Control Action":
                label = format_control_flow_label(conn_obj, repo, "Control Flow Diagram")
                if label:
                    actions.append(label)
        return sorted(actions)

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, row=None):
            self.parent = parent
            self.app = parent.app
            self.row = row or StpaEntry("", "", "", "", "", [])
            super().__init__(parent, title="Edit STPA Row")

        def body(self, master):
            ttk.Label(master, text="Action").grid(row=0, column=0, sticky="e")
            actions = self.parent._get_actions()
            self.action_var = tk.StringVar(value=self.row.action)
            action_cb = ttk.Combobox(
                master, textvariable=self.action_var, values=actions, state="readonly"
            )
            action_cb.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(master, text="Not Providing causes Hazard").grid(
                row=1, column=0, sticky="e"
            )
            self.np_var = tk.Entry(master, width=40)
            self.np_var.insert(0, self.row.not_providing)
            self.np_var.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(master, text="Providing causes Hazard").grid(
                row=2, column=0, sticky="e"
            )
            self.p_var = tk.Entry(master, width=40)
            self.p_var.insert(0, self.row.providing)
            self.p_var.grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(master, text="Incorrect Timing/Order").grid(
                row=3, column=0, sticky="e"
            )
            self.it_var = tk.Entry(master, width=40)
            self.it_var.insert(0, self.row.incorrect_timing)
            self.it_var.grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(master, text="Stopped Too Soon/ Applied Too Long").grid(
                row=4, column=0, sticky="e"
            )
            self.st_var = tk.Entry(master, width=40)
            self.st_var.insert(0, self.row.stopped_too_soon)
            self.st_var.grid(row=4, column=1, padx=5, pady=5)

            ttk.Label(master, text="Safety Constraints").grid(row=5, column=0, sticky="ne")
            sc_frame = ttk.Frame(master)
            sc_frame.grid(row=5, column=1, padx=5, pady=5)
            self.sc_lb = tk.Listbox(sc_frame, selectmode="extended", height=4, width=40)
            self.sc_lb.grid(row=0, column=0, columnspan=4)
            for rid in self.row.safety_constraints:
                req = global_requirements.get(rid, {"text": ""})
                self.sc_lb.insert(tk.END, f"[{rid}] {req.get('text','')}")
            ttk.Button(sc_frame, text="Add New", command=self.add_sc_new).grid(
                row=1, column=0
            )
            ttk.Button(sc_frame, text="Add Existing", command=self.add_sc_existing).grid(
                row=1, column=1
            )
            ttk.Button(sc_frame, text="Edit", command=self.edit_sc).grid(row=1, column=2)
            ttk.Button(sc_frame, text="Delete", command=self.del_sc).grid(row=1, column=3)
            return action_cb

        def _ask_type(self):
            rt = simpledialog.askstring(
                "Requirement Type", "Type:", initialvalue=REQUIREMENT_TYPE_OPTIONS[0]
            )
            if not rt:
                return None
            rt = rt.strip().lower()
            if rt not in REQUIREMENT_TYPE_OPTIONS:
                messagebox.showerror("Requirement", "Invalid type")
                return None
            return rt

        def add_sc_new(self):
            rt = self._ask_type()
            if not rt:
                return
            dlg = _RequirementDialog(self, req_type=rt)
            if dlg.result:
                req = dlg.result
                global_requirements[req["id"]] = req
                self.sc_lb.insert(tk.END, f"[{req['id']}] {req['text']}")

        def add_sc_existing(self):
            rt = self._ask_type()
            if not rt:
                return
            dlg = _SelectRequirementsDialog(self, req_type=rt)
            if dlg.result:
                for val in dlg.result:
                    if val not in self.sc_lb.get(0, tk.END):
                        self.sc_lb.insert(tk.END, val)

        def edit_sc(self):
            sel = self.sc_lb.curselection()
            if not sel:
                return
            text = self.sc_lb.get(sel[0])
            rid = text.split("]", 1)[0][1:]
            req = global_requirements.get(
                rid, {"id": rid, "text": text, "req_type": "operational"}
            )
            dlg = _RequirementDialog(self, req, req_type=req.get("req_type", "operational"))
            if dlg.result:
                req = dlg.result
                global_requirements[req["id"]] = req
                self.sc_lb.delete(sel[0])
                self.sc_lb.insert(sel[0], f"[{req['id']}] {req['text']}")

        def del_sc(self):
            for idx in reversed(self.sc_lb.curselection()):
                self.sc_lb.delete(idx)

        def apply(self):
            self.row.action = self.action_var.get()
            self.row.not_providing = self.np_var.get()
            self.row.providing = self.p_var.get()
            self.row.incorrect_timing = self.it_var.get()
            self.row.stopped_too_soon = self.st_var.get()
            self.row.safety_constraints = [
                self.sc_lb.get(i).split("]", 1)[0][1:]
                for i in range(self.sc_lb.size())
            ]

    def add_row(self):
        if not self.app.active_stpa:
            messagebox.showwarning("Add", "Create an STPA first")
            return
        dlg = self.RowDialog(self)
        if getattr(dlg, "row", None):
            self.app.stpa_entries.append(dlg.row)
        self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        self.RowDialog(self, self.app.stpa_entries[idx])
        self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.stpa_entries):
                del self.app.stpa_entries[idx]
        self.refresh()

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        if row >= len(self.app.stpa_entries):
            return
        entry = self.app.stpa_entries[row]
        if column == "safety_constraints":
            entry.safety_constraints = [v for v in value.split(";") if v]
        elif column in self.COLS:
            setattr(entry, column, value)
        self.refresh()

