# Author: ChatGPT
import tkinter as tk
from tkinter import ttk, simpledialog

from gui import messagebox
from gui.toolboxes import configure_table_style, ToolTip
from analysis.models import (
    DamageScenario,
    ThreatScenario,
    AttackPath,
    ThreatDoc,
)
from sysml.sysml_repository import SysMLRepository


class ThreatWindow(tk.Frame):
    """UI for Threat Analysis documents."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("Threat Analysis")
            master.geometry("700x500")

        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Threat:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        # Asset Identification tab -------------------------------------------------
        asset_tab = ttk.Frame(nb)
        nb.add(asset_tab, text="Asset Identification")

        ai_top = ttk.Frame(asset_tab)
        ai_top.pack(fill=tk.X)
        ttk.Label(ai_top, text="Asset:").pack(side=tk.LEFT)
        self.asset_var = tk.StringVar()
        self.asset_cb = ttk.Combobox(ai_top, textvariable=self.asset_var, state="readonly")
        self.asset_cb.pack(side=tk.LEFT, padx=2)
        self.asset_cb.bind("<<ComboboxSelected>>", self._asset_changed)
        ttk.Label(ai_top, text="Function:").pack(side=tk.LEFT)
        self.func_var = tk.StringVar()
        self.func_cb = ttk.Combobox(ai_top, textvariable=self.func_var, state="readonly")
        self.func_cb.pack(side=tk.LEFT, padx=2)
        self.func_cb.bind("<<ComboboxSelected>>", self._func_changed)

        ds_frame = ttk.Frame(asset_tab)
        ds_frame.pack(fill=tk.BOTH, expand=True)
        configure_table_style("Threat.Damage")
        self.ds_tree = ttk.Treeview(
            ds_frame, columns=("scenario", "type"), show="headings", style="Threat.Damage"
        )
        self.ds_tree.heading("scenario", text="Scenario")
        self.ds_tree.heading("type", text="Type")
        self.ds_tree.column("scenario", width=250)
        self.ds_tree.column("type", width=100)
        self.ds_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ds_scroll = ttk.Scrollbar(ds_frame, orient="vertical", command=self.ds_tree.yview)
        self.ds_tree.configure(yscrollcommand=ds_scroll.set)
        ds_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ds_btn = ttk.Frame(asset_tab)
        ds_btn.pack(fill=tk.X)
        ttk.Button(ds_btn, text="Add", command=self.add_damage_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ds_btn, text="Edit", command=self.edit_damage_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ds_btn, text="Delete", command=self.del_damage_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )

        # Threat Analysis tab ------------------------------------------------------
        threat_tab = ttk.Frame(nb)
        nb.add(threat_tab, text="Threat Analysis")

        ta_frame = ttk.Frame(threat_tab)
        ta_frame.pack(fill=tk.BOTH, expand=True)
        configure_table_style("Threat.Scenarios")
        self.threat_tree = ttk.Treeview(
            ta_frame,
            columns=("stride", "scenario"),
            show="headings",
            style="Threat.Scenarios",
            height=6,
        )
        self.threat_tree.heading("stride", text="STRIDE")
        self.threat_tree.heading("scenario", text="Scenario")
        self.threat_tree.column("stride", width=100)
        self.threat_tree.column("scenario", width=250)
        self.threat_tree.bind("<<TreeviewSelect>>", self.on_threat_select)
        self.threat_tree.grid(row=0, column=0, sticky="nsew")
        tscroll = ttk.Scrollbar(ta_frame, orient="vertical", command=self.threat_tree.yview)
        self.threat_tree.configure(yscrollcommand=tscroll.set)
        tscroll.grid(row=0, column=1, sticky="ns")

        configure_table_style("Threat.Paths")
        self.path_tree = ttk.Treeview(
            ta_frame,
            columns=("path",),
            show="headings",
            style="Threat.Paths",
            height=4,
        )
        self.path_tree.heading("path", text="Attack Path")
        self.path_tree.column("path", width=350)
        self.path_tree.grid(row=1, column=0, sticky="nsew")
        pscroll = ttk.Scrollbar(ta_frame, orient="vertical", command=self.path_tree.yview)
        self.path_tree.configure(yscrollcommand=pscroll.set)
        pscroll.grid(row=1, column=1, sticky="ns")

        ta_frame.columnconfigure(0, weight=1)
        ta_frame.rowconfigure(0, weight=1)
        ta_frame.rowconfigure(1, weight=1)

        ta_btn = ttk.Frame(threat_tab)
        ta_btn.pack(fill=tk.X)
        ttk.Button(ta_btn, text="Add", command=self.add_threat_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ta_btn, text="Edit", command=self.edit_threat_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ta_btn, text="Delete", command=self.del_threat_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ta_btn, text="Add Path", command=self.add_attack_path).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ta_btn, text="Edit Path", command=self.edit_attack_path).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ta_btn, text="Delete Path", command=self.del_attack_path).pack(
            side=tk.LEFT, padx=2, pady=2
        )

        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_assets(self):
        repo = SysMLRepository.get_instance()
        items = list(repo.parts.keys()) + list(repo.ports.keys()) + list(repo.flows.keys()) + list(repo.connectors.keys())
        return sorted(items)

    def _get_functions(self):
        repo = SysMLRepository.get_instance()
        actions = [a.name for a in repo.actions.values()]
        activities = [a.name for a in repo.activities.values()]
        return sorted(set(actions + activities))

    def _asset_changed(self, *_):
        if self.app.active_threat:
            self.app.active_threat.asset = self.asset_var.get()

    def _func_changed(self, *_):
        if self.app.active_threat:
            self.app.active_threat.function = self.func_var.get()

    # ------------------------------------------------------------------
    # Document management
    # ------------------------------------------------------------------
    def refresh_docs(self):
        names = [d.name for d in self.app.threat_docs]
        self.doc_cb["values"] = names
        self.asset_cb["values"] = self._get_assets()
        self.func_cb["values"] = self._get_functions()
        if self.app.active_threat:
            self.doc_var.set(self.app.active_threat.name)
            self.asset_var.set(self.app.active_threat.asset)
            self.func_var.set(self.app.active_threat.function)
        elif names:
            self.doc_var.set(names[0])
            self.app.active_threat = self.app.threat_docs[0]
            self.asset_var.set(self.app.active_threat.asset)
            self.func_var.set(self.app.active_threat.function)

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.threat_docs:
            if d.name == name:
                self.app.active_threat = d
                break
        if self.app.active_threat:
            self.asset_var.set(self.app.active_threat.asset)
            self.func_var.set(self.app.active_threat.function)
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New Threat Analysis", "Name:")
        if not name:
            return
        doc = ThreatDoc(name, "", "", [], [])
        self.app.threat_docs.append(doc)
        self.app.active_threat = doc
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
        if not messagebox.askyesno("Delete", f"Delete Threat Analysis '{doc.name}'?"):
            return
        self.app.threat_docs.remove(doc)
        if self.app.threat_docs:
            self.app.active_threat = self.app.threat_docs[0]
        else:
            self.app.active_threat = None
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------
    def refresh(self):
        self.ds_tree.delete(*self.ds_tree.get_children())
        self.threat_tree.delete(*self.threat_tree.get_children())
        self.path_tree.delete(*self.path_tree.get_children())
        doc = self.app.active_threat
        if not doc:
            return
        for ds in doc.damage_scenarios:
            self.ds_tree.insert("", "end", values=(ds.scenario, ds.type))
        for idx, ts in enumerate(doc.threat_scenarios):
            self.threat_tree.insert("", "end", iid=str(idx), values=(ts.stride, ts.scenario))

    def on_threat_select(self, _event=None):
        self.path_tree.delete(*self.path_tree.get_children())
        sel = self.threat_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        ts = self.app.active_threat.threat_scenarios[idx]
        for ap in ts.attack_paths:
            self.path_tree.insert("", "end", values=(ap.description,))

    # ------------------------------------------------------------------
    # Damage scenarios operations
    # ------------------------------------------------------------------
    def add_damage_scenario(self):
        scenario = simpledialog.askstring("Damage Scenario", "Description:")
        if not scenario:
            return
        stype = simpledialog.askstring("Damage Scenario", "Type:", initialvalue="")
        if stype is None:
            return
        self.app.active_threat.damage_scenarios.append(DamageScenario(scenario, stype))
        self.refresh()

    def edit_damage_scenario(self):
        sel = self.ds_tree.selection()
        if not sel:
            return
        idx = self.ds_tree.index(sel[0])
        ds = self.app.active_threat.damage_scenarios[idx]
        scenario = simpledialog.askstring("Damage Scenario", "Description:", initialvalue=ds.scenario)
        if not scenario:
            return
        stype = simpledialog.askstring("Damage Scenario", "Type:", initialvalue=ds.type)
        if stype is None:
            return
        ds.scenario = scenario
        ds.type = stype
        self.refresh()

    def del_damage_scenario(self):
        sel = self.ds_tree.selection()
        if not sel:
            return
        idx = self.ds_tree.index(sel[0])
        del self.app.active_threat.damage_scenarios[idx]
        self.refresh()

    # ------------------------------------------------------------------
    # Threat scenarios operations
    # ------------------------------------------------------------------
    def add_threat_scenario(self):
        stride = simpledialog.askstring("Threat Scenario", "STRIDE Category:")
        if not stride:
            return
        scenario = simpledialog.askstring("Threat Scenario", "Scenario:")
        if not scenario:
            return
        self.app.active_threat.threat_scenarios.append(
            ThreatScenario(stride, scenario, [])
        )
        self.refresh()

    def edit_threat_scenario(self):
        sel = self.threat_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        ts = self.app.active_threat.threat_scenarios[idx]
        stride = simpledialog.askstring("Threat Scenario", "STRIDE Category:", initialvalue=ts.stride)
        if not stride:
            return
        scenario = simpledialog.askstring("Threat Scenario", "Scenario:", initialvalue=ts.scenario)
        if not scenario:
            return
        ts.stride = stride
        ts.scenario = scenario
        self.refresh()
        self.on_threat_select()

    def del_threat_scenario(self):
        sel = self.threat_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.app.active_threat.threat_scenarios[idx]
        self.refresh()
        self.path_tree.delete(*self.path_tree.get_children())

    # ------------------------------------------------------------------
    # Attack path operations
    # ------------------------------------------------------------------
    def add_attack_path(self):
        sel = self.threat_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        ts = self.app.active_threat.threat_scenarios[idx]
        desc = simpledialog.askstring("Attack Path", "Path:")
        if not desc:
            return
        ts.attack_paths.append(AttackPath(desc))
        self.on_threat_select()

    def edit_attack_path(self):
        sel = self.threat_tree.selection()
        if not sel:
            return
        t_idx = int(sel[0])
        ts = self.app.active_threat.threat_scenarios[t_idx]
        sel_p = self.path_tree.selection()
        if not sel_p:
            return
        p_idx = self.path_tree.index(sel_p[0])
        ap = ts.attack_paths[p_idx]
        desc = simpledialog.askstring("Attack Path", "Path:", initialvalue=ap.description)
        if not desc:
            return
        ap.description = desc
        self.on_threat_select()

    def del_attack_path(self):
        sel = self.threat_tree.selection()
        if not sel:
            return
        t_idx = int(sel[0])
        ts = self.app.active_threat.threat_scenarios[t_idx]
        sel_p = self.path_tree.selection()
        if not sel_p:
            return
        p_idx = self.path_tree.index(sel_p[0])
        del ts.attack_paths[p_idx]
        self.on_threat_select()
