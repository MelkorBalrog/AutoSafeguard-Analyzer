# Author: ChatGPT
import tkinter as tk
from tkinter import ttk, simpledialog

from gui import messagebox
from gui.toolboxes import ToolTip, configure_table_style
from analysis.models import ThreatDoc, ThreatEntry
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
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

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
        names = [d.name for d in self.app.threat_docs]
        self.doc_cb["values"] = names
        if self.app.active_threat:
            self.doc_var.set(self.app.active_threat.name)
        elif names:
            self.doc_var.set(names[0])
            self.select_doc()

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.threat_docs:
            if d.name == name:
                self.app.active_threat = d
                self.app.threat_entries = d.entries
                break
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New Threat Analysis", "Name:")
        if not name:
            return
        doc = ThreatDoc(name, [])
        self.app.threat_docs.append(doc)
        self.app.active_threat = doc
        self.app.threat_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_threat:
            return
        name = simpledialog.askstring(
            "Rename Threat Analysis", "Name:", initialvalue=self.app.active_threat.name
        )
        if not name:
            return
        self.app.active_threat.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_threat
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete Threat '{doc.name}'?"):
            return
        self.app.threat_docs.remove(doc)
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
