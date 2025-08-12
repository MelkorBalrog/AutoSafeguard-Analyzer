import tkinter as tk
from tkinter import ttk, simpledialog
from gui.tooltip import ToolTip
from gui.toolboxes import EditableTreeview, configure_table_style
from analysis.models import DamageScenario, ThreatDoc


class ThreatWindow(tk.Frame):
    """UI for creating and editing threat analyses."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("Threat Analysis")
            master.geometry("800x600")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Threat Doc:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        new_btn = ttk.Button(top, text="New", command=self.new_doc)
        new_btn.pack(side=tk.LEFT)
        edit_btn = ttk.Button(top, text="Rename", command=self.rename_doc)
        edit_btn.pack(side=tk.LEFT)
        del_btn = ttk.Button(top, text="Delete", command=self.delete_doc)
        del_btn.pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        # Asset Identification tab
        asset_tab = ttk.Frame(self.nb)
        self.nb.add(asset_tab, text="Asset Identification")
        combo = ttk.Frame(asset_tab)
        combo.pack(fill=tk.X, pady=2)
        self.part_cb = ttk.Combobox(combo, state="readonly", width=20)
        self.port_cb = ttk.Combobox(combo, state="readonly", width=20)
        self.flow_cb = ttk.Combobox(combo, state="readonly", width=20)
        self.conn_cb = ttk.Combobox(combo, state="readonly", width=20)
        self.action_cb = ttk.Combobox(combo, state="readonly", width=20)
        self.activity_cb = ttk.Combobox(combo, state="readonly", width=20)
        ttk.Label(combo, text="Part:").grid(row=0, column=0, padx=2, pady=2)
        self.part_cb.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(combo, text="Port:").grid(row=0, column=2, padx=2, pady=2)
        self.port_cb.grid(row=0, column=3, padx=2, pady=2)
        ttk.Label(combo, text="Flow:").grid(row=1, column=0, padx=2, pady=2)
        self.flow_cb.grid(row=1, column=1, padx=2, pady=2)
        ttk.Label(combo, text="Connector:").grid(row=1, column=2, padx=2, pady=2)
        self.conn_cb.grid(row=1, column=3, padx=2, pady=2)
        ttk.Label(combo, text="Action:").grid(row=2, column=0, padx=2, pady=2)
        self.action_cb.grid(row=2, column=1, padx=2, pady=2)
        ttk.Label(combo, text="Activity:").grid(row=2, column=2, padx=2, pady=2)
        self.activity_cb.grid(row=2, column=3, padx=2, pady=2)

        columns = ("asset", "function", "category", "description")
        configure_table_style("ThreatAsset.Treeview")
        self.asset_tree = EditableTreeview(
            asset_tab,
            columns=columns,
            show="headings",
            style="ThreatAsset.Treeview",
            height=8,
        )
        for col in columns:
            self.asset_tree.heading(col, text=col.capitalize())
            self.asset_tree.column(col, width=150)
        self.asset_tree.pack(fill=tk.BOTH, expand=True)
        btn = ttk.Frame(asset_tab)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text="Add", command=self.add_damage).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Edit", command=self.edit_damage).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Delete", command=self.del_damage).pack(side=tk.LEFT, padx=2, pady=2)

        # Threat Analysis tab
        threat_tab = ttk.Frame(self.nb)
        self.nb.add(threat_tab, text="Threat Analysis")
        self.threat_tree = ttk.Treeview(
            threat_tab,
            columns=("type", "description"),
            show="tree headings",
            height=8,
        )
        self.threat_tree.heading("type", text="Type")
        self.threat_tree.heading("description", text="Description")
        self.threat_tree.column("type", width=120)
        self.threat_tree.column("description", width=300)
        self.threat_tree.pack(fill=tk.BOTH, expand=True)
        tbtn = ttk.Frame(threat_tab)
        tbtn.pack(fill=tk.X)
        ttk.Button(tbtn, text="Add", command=self.add_threat).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(tbtn, text="Edit", command=self.edit_threat).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(tbtn, text="Delete", command=self.del_threat).pack(side=tk.LEFT, padx=2, pady=2)

        self.refresh_docs()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    # --- Document management ---
    def refresh_docs(self):
        names = [d.name for d in self.app.threat_docs]
        self.doc_cb["values"] = names
        if self.app.active_threat:
            self.doc_var.set(self.app.active_threat.name)
        elif names:
            self.doc_var.set(names[0])

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.threat_docs:
            if d.name == name:
                self.app.active_threat = d
                break

    def new_doc(self):
        name = simpledialog.askstring("New Threat Doc", "Name:")
        if not name:
            return
        doc = ThreatDoc(name, [])
        self.app.threat_docs.append(doc)
        self.app.active_threat = doc
        self.refresh_docs()

    def rename_doc(self):
        if not self.app.active_threat:
            return
        name = simpledialog.askstring(
            "Rename Threat Doc", "Name:", initialvalue=self.app.active_threat.name
        )
        if not name:
            return
        self.app.active_threat.name = name
        self.refresh_docs()

    def delete_doc(self):
        doc = self.app.active_threat
        if not doc:
            return
        if doc in self.app.threat_docs:
            self.app.threat_docs.remove(doc)
        self.app.active_threat = self.app.threat_docs[0] if self.app.threat_docs else None
        self.refresh_docs()

    # --- Damage scenario operations ---
    def add_damage(self):
        ds = DamageScenario("", "", "Confidentiality", "")
        if not self.app.active_threat:
            return
        self.app.active_threat.damages.append(ds)
        self.asset_tree.insert("", tk.END, values=(ds.asset, ds.function, ds.category, ds.description))

    def edit_damage(self):
        item = self.asset_tree.focus()
        if not item or not self.app.active_threat:
            return
        idx = self.asset_tree.index(item)
        ds = self.app.active_threat.damages[idx]
        text = simpledialog.askstring("Edit Description", "Description:", initialvalue=ds.description)
        if text is not None:
            ds.description = text
            self.asset_tree.set(item, "description", text)

    def del_damage(self):
        item = self.asset_tree.focus()
        if not item or not self.app.active_threat:
            return
        idx = self.asset_tree.index(item)
        del self.app.active_threat.damages[idx]
        self.asset_tree.delete(item)

    # --- Threat scenario operations (stubs) ---
    def add_threat(self):
        pass

    def edit_threat(self):
        pass

    def del_threat(self):
        sel = self.threat_tree.focus()
        if sel:
            self.threat_tree.delete(sel)
