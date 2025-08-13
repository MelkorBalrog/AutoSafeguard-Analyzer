# Author: ChatGPT
import tkinter as tk
from tkinter import ttk, simpledialog

from gui import messagebox
from gui.toolboxes import ToolTip, configure_table_style
from analysis.models import ThreatDoc, ThreatEntry
from sysml.sysml_repository import SysMLRepository
from gui.architecture import format_diagram_name
from .threat_dialog import ThreatDialog


class ThreatWindow(tk.Frame):
    """Main window for Threat Analysis documents."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("Threat Analysis")
            master.geometry("700x350")
            master.resizable(False, False)

        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Threat:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ToolTip(self.doc_cb, "Select a Threat Analysis document to edit.")
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Edit", command=self.edit_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)
        self.diag_lbl = ttk.Label(top, text="")
        self.diag_lbl.pack(side=tk.LEFT, padx=10)

        columns = ("asset", "functions", "damage", "type", "threat", "path")
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True)
        configure_table_style("Threat.Treeview")
        self.tree = ttk.Treeview(
            content,
            columns=columns,
            show="headings",
            style="Threat.Treeview",
            height=8,
        )
        headers = {
            "asset": "Asset",
            "functions": "Functions",
            "damage": "Damage Scenario",
            "type": "Damage Type",
            "threat": "Threat Scenario (STRIDE)",
            "path": "Attack Paths",
        }
        for col in columns:
            self.tree.heading(col, text=headers[col])
            width = 120 if col in {"asset", "functions", "type"} else 200
            self.tree.column(col, width=width, stretch=True)
        vsb = ttk.Scrollbar(content, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        self.tree.bind("<Double-1>", self.on_double_click)

        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        add_btn = ttk.Button(btn, text="Add", command=self.add_row)
        add_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(add_btn, "Insert a new Threat Analysis entry.")
        edit_btn = ttk.Button(btn, text="Edit", command=self.edit_row)
        edit_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(edit_btn, "Edit the selected Threat Analysis entry.")
        del_btn = ttk.Button(btn, text="Delete", command=self.del_row)
        del_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(del_btn, "Remove the selected Threat Analysis entry.")

        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Document management
    # ------------------------------------------------------------------
    def refresh_docs(self):
        toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
        names = [
            d.name
            for d in self.app.threat_docs
            if not toolbox or toolbox.document_visible("Threat Analysis", d.name)
        ]
        self.doc_cb["values"] = names
        if (
            self.app.active_threat
            and self.app.active_threat.name in names
        ):
            self.doc_var.set(self.app.active_threat.name)
            repo = SysMLRepository.get_instance()
            diag = repo.diagrams.get(self.app.active_threat.diagram)
            self.diag_lbl.config(text=f"Diagram: {format_diagram_name(diag)}")
        elif names:
            self.doc_var.set(names[0])
            self.select_doc()
        else:
            self.doc_var.set("")
            self.app.active_threat = None
            self.app.threat_entries = []
            self.diag_lbl.config(text="")

    def select_doc(self, *_):
        name = self.doc_var.get()
        repo = SysMLRepository.get_instance()
        for d in self.app.threat_docs:
            if d.name == name:
                self.app.active_threat = d
                self.app.threat_entries = d.entries
                diag = repo.diagrams.get(d.diagram)
                self.diag_lbl.config(text=f"Diagram: {format_diagram_name(diag)}")
                break
        self.refresh()

    class NewThreatDialog(simpledialog.Dialog):
        def __init__(self, parent, app):
            self.app = app
            super().__init__(parent, title="New Threat Analysis")

        def body(self, master):
            ttk.Label(master, text="Name").grid(row=0, column=0, sticky="e")
            self.name_var = tk.StringVar()
            name_entry = ttk.Entry(master, textvariable=self.name_var)
            name_entry.grid(row=0, column=1)
            ttk.Label(master, text="Internal Block Diagram").grid(
                row=1, column=0, sticky="e"
            )
            repo = SysMLRepository.get_instance()
            self.diag_map = {}
            diags = []
            for d in repo.diagrams.values():
                if d.diag_type != "Internal Block Diagram":
                    continue
                disp = format_diagram_name(d)
                self.diag_map[disp] = d.diag_id
                diags.append(disp)
            self.diag_var = tk.StringVar()
            ttk.Combobox(
                master, textvariable=self.diag_var, values=diags, state="readonly"
            ).grid(row=1, column=1)
            return name_entry

        def apply(self):
            self.result = (
                self.name_var.get(), self.diag_map.get(self.diag_var.get(), "")
            )

    class EditThreatDialog(simpledialog.Dialog):
        def __init__(self, parent, app):
            self.app = app
            super().__init__(parent, title="Edit Threat Analysis")

        def body(self, master):
            self._body = master
            ttk.Label(master, text="Internal Block Diagram").grid(
                row=0, column=0, sticky="e"
            )
            repo = SysMLRepository.get_instance()
            self.diag_map = {}
            diags = []
            for d in repo.diagrams.values():
                if d.diag_type != "Internal Block Diagram":
                    continue
                disp = format_diagram_name(d)
                self.diag_map[disp] = d.diag_id
                diags.append(disp)
            self.diag_var = tk.StringVar()
            ttk.Combobox(
                master, textvariable=self.diag_var, values=diags, state="readonly"
            ).grid(row=0, column=1)
            current = ""
            if self.app.active_threat:
                diag = repo.diagrams.get(self.app.active_threat.diagram)
                current = format_diagram_name(diag) if diag else ""
            if current:
                self.diag_var.set(current)
            return master

        def buttonbox(self):
            """Place explicit OK/Cancel buttons at the bottom."""
            if hasattr(self, "_body"):
                self._body.pack_configure(fill=tk.BOTH, expand=True)

            box = ttk.Frame(self)
            box.pack(fill=tk.X, padx=5, pady=5)

            ok_btn = ttk.Button(
                box, text="OK", width=10, command=self.ok, default=tk.ACTIVE
            )
            ok_btn.pack(side=tk.RIGHT, padx=5)
            cancel_btn = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            ok_btn.focus_set()
            self.bind("<Return>", self.ok)
            self.bind("<Escape>", self.cancel)

        def apply(self):
            self.result = self.diag_map.get(self.diag_var.get(), "")

    def new_doc(self):
        dlg = self.NewThreatDialog(self, self.app)
        if not getattr(dlg, "result", None):
            return
        name, diag_id = dlg.result
        doc = ThreatDoc(name, diag_id, [])
        self.app.threat_docs.append(doc)
        self.app.active_threat = doc
        self.app.threat_entries = doc.entries
        # Record the creation phase for lifecycle filtering
        if hasattr(self.app, "safety_mgmt_toolbox"):
            self.app.safety_mgmt_toolbox.register_created_work_product(
                "Threat Analysis", doc.name
            )
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_threat:
            return
        old = self.app.active_threat.name
        name = simpledialog.askstring(
            "Rename Threat Analysis", "Name:", initialvalue=old
        )
        if not name:
            return
        self.app.active_threat.name = name
        if hasattr(self.app, "safety_mgmt_toolbox"):
            self.app.safety_mgmt_toolbox.rename_document(
                "Threat Analysis", old, name
            )
        self.refresh_docs()
        self.app.update_views()

    def edit_doc(self):
        if not self.app.active_threat:
            return
        dlg = self.EditThreatDialog(self, self.app)
        if not getattr(dlg, "result", None):
            return
        repo = SysMLRepository.get_instance()
        diag_id = dlg.result
        self.app.active_threat.diagram = diag_id
        self.app.threat_entries = self.app.active_threat.entries
        diag = repo.diagrams.get(diag_id)
        self.diag_lbl.config(text=f"Diagram: {format_diagram_name(diag)}")
        self.refresh()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_threat
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete Threat '{doc.name}'?"):
            return
        self.app.threat_docs.remove(doc)
        if hasattr(self.app, "safety_mgmt_toolbox"):
            self.app.safety_mgmt_toolbox.register_deleted_work_product(
                "Threat Analysis", doc.name
            )
        if self.app.threat_docs:
            self.app.active_threat = self.app.threat_docs[0]
            self.app.threat_entries = self.app.active_threat.entries
        else:
            self.app.active_threat = None
            self.app.threat_entries = []
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    # ------------------------------------------------------------------
    # Table actions
    # ------------------------------------------------------------------
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for idx, entry in enumerate(self.app.threat_entries):
            funcs = [f.name for f in entry.functions]
            damages = "; ".join(
                ds.scenario for f in entry.functions for ds in f.damage_scenarios
            )
            types = "; ".join(
                ds.dtype for f in entry.functions for ds in f.damage_scenarios
            )
            threats = "; ".join(
                f"{ts.stride}: {ts.scenario}"
                for f in entry.functions
                for ds in f.damage_scenarios
                for ts in ds.threats
            )
            paths = "; ".join(
                ap.description
                for f in entry.functions
                for ds in f.damage_scenarios
                for ts in ds.threats
                for ap in ts.attack_paths
            )
            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    entry.asset,
                    "; ".join(funcs),
                    damages,
                    types,
                    threats,
                    paths,
                ),
            )

    def on_double_click(self, *_):
        self.edit_row()

    def add_row(self):
        dlg = ThreatDialog(self, self.app)
        if dlg.result:
            self.app.threat_entries.append(dlg.result)
            self.refresh()

    def edit_row(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        entry = self.app.threat_entries[idx]
        dlg = ThreatDialog(self, self.app, entry)
        if dlg.result:
            self.app.threat_entries[idx] = dlg.result
            self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.app.threat_entries[idx]
        self.refresh()
