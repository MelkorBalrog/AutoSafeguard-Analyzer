# Author: ChatGPT
import tkinter as tk
from tkinter import ttk, simpledialog

from gui import messagebox
from gui.toolboxes import configure_table_style
from analysis.models import (
    AttackPath,
    DamageScenario,
    ThreatScenario,
    ThreatEntry,
)
from sysml.sysml_repository import SysMLRepository


class ThreatDialog(simpledialog.Dialog):
    """Dialog for creating or editing a threat analysis entry."""

    def __init__(self, parent, app, entry=None):
        self.app = app
        self.entry = entry if entry else ThreatEntry("", "", [])
        super().__init__(parent, title="Edit Threat Entry")

    # ------------------------------------------------------------------
    def body(self, master):
        nb = ttk.Notebook(master)
        nb.pack(fill=tk.BOTH, expand=True)

        # Asset Identification tab --------------------------------------
        asset_tab = ttk.Frame(nb)
        nb.add(asset_tab, text="Asset Identification")

        ai_top = ttk.Frame(asset_tab)
        ai_top.pack(fill=tk.X)
        ttk.Label(ai_top, text="Asset:").pack(side=tk.LEFT)
        self.asset_var = tk.StringVar(value=self.entry.asset)
        self.asset_cb = ttk.Combobox(
            ai_top,
            textvariable=self.asset_var,
            values=self._get_assets(),
            state="readonly",
        )
        self.asset_cb.pack(side=tk.LEFT, padx=2)
        ttk.Label(ai_top, text="Function:").pack(side=tk.LEFT)
        self.func_var = tk.StringVar(value=self.entry.function)
        self.func_cb = ttk.Combobox(
            ai_top,
            textvariable=self.func_var,
            values=self._get_functions(),
            state="readonly",
        )
        self.func_cb.pack(side=tk.LEFT, padx=2)

        ds_frame = ttk.Frame(asset_tab)
        ds_frame.pack(fill=tk.BOTH, expand=True)
        configure_table_style("Threat.Damage.Treeview")
        self.ds_tree = ttk.Treeview(
            ds_frame,
            columns=("scenario", "type"),
            show="headings",
            style="Threat.Damage.Treeview",
        )
        self.ds_tree.heading("scenario", text="Scenario")
        self.ds_tree.heading("type", text="Type")
        self.ds_tree.column("scenario", width=250)
        self.ds_tree.column("type", width=100)
        self.ds_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ds_scroll = ttk.Scrollbar(ds_frame, orient="vertical", command=self.ds_tree.yview)
        self.ds_tree.configure(yscrollcommand=ds_scroll.set)
        ds_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ds_tree.bind("<<TreeviewSelect>>", self.on_ds_select)

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

        # Threat Analysis tab -------------------------------------------
        threat_tab = ttk.Frame(nb)
        nb.add(threat_tab, text="Threat Analysis")

        ta_frame = ttk.Frame(threat_tab)
        ta_frame.pack(fill=tk.BOTH, expand=True)
        configure_table_style("Threat.Scenarios.Treeview")
        self.threat_tree = ttk.Treeview(
            ta_frame,
            columns=("stride", "scenario"),
            show="headings",
            style="Threat.Scenarios.Treeview",
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

        configure_table_style("Threat.Paths.Treeview")
        self.path_tree = ttk.Treeview(
            ta_frame,
            columns=("path",),
            show="headings",
            style="Threat.Paths.Treeview",
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

        self.refresh_ds()
        return nb

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def _get_assets(self):
        repo = SysMLRepository.get_instance()
        names = set()
        for elem in repo.elements.values():
            if elem.elem_type in {"Part", "Port", "Flow", "Connector"} and elem.name:
                names.add(elem.name)
        for diag in repo.diagrams.values():
            for obj in getattr(diag, "objects", []):
                typ = obj.get("obj_type") or obj.get("type")
                if typ in {"Part", "Port", "Flow", "Connector"}:
                    name = obj.get("properties", {}).get("name")
                    if not name:
                        elem_id = obj.get("element_id")
                        if elem_id and elem_id in repo.elements:
                            name = repo.elements[elem_id].name
                    if name:
                        names.add(name)
        return sorted(names)

    def _get_functions(self):
        return self.app.get_all_action_names()

    # ------------------------------------------------------------------
    def on_ds_select(self, *_):
        self.refresh_threats()

    def on_threat_select(self, *_):
        self.refresh_paths()

    def refresh_ds(self):
        self.ds_tree.delete(*self.ds_tree.get_children())
        for idx, ds in enumerate(self.entry.damage_scenarios):
            self.ds_tree.insert("", "end", iid=str(idx), values=(ds.scenario, ds.dtype))
        self.refresh_threats()

    def refresh_threats(self):
        self.threat_tree.delete(*self.threat_tree.get_children())
        self.path_tree.delete(*self.path_tree.get_children())
        sel = self.ds_tree.selection()
        if not sel:
            return
        ds = self.entry.damage_scenarios[int(sel[0])]
        for idx, ts in enumerate(ds.threats):
            self.threat_tree.insert("", "end", iid=str(idx), values=(ts.stride, ts.scenario))
        self.refresh_paths()

    def refresh_paths(self):
        self.path_tree.delete(*self.path_tree.get_children())
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if not ds_sel or not ts_sel:
            return
        ds = self.entry.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        for idx, ap in enumerate(ts.attack_paths):
            self.path_tree.insert("", "end", iid=str(idx), values=(ap.description,))

    # ------------------------------------------------------------------
    # Damage Scenarios
    # ------------------------------------------------------------------
    def add_damage_scenario(self):
        scenario = simpledialog.askstring("Damage Scenario", "Scenario:", parent=self)
        if not scenario:
            return
        stype = simpledialog.askstring(
            "Damage Scenario",
            "Type (Confidentiality, Integrity, Availability):",
            parent=self,
        )
        if stype is None:
            stype = ""
        self.entry.damage_scenarios.append(DamageScenario(scenario, stype))
        self.refresh_ds()

    def edit_damage_scenario(self):
        sel = self.ds_tree.selection()
        if not sel:
            messagebox.showwarning("Edit", "Select a damage scenario")
            return
        idx = int(sel[0])
        ds = self.entry.damage_scenarios[idx]
        scenario = simpledialog.askstring(
            "Damage Scenario", "Scenario:", initialvalue=ds.scenario, parent=self
        )
        if not scenario:
            return
        stype = simpledialog.askstring(
            "Damage Scenario",
            "Type (Confidentiality, Integrity, Availability):",
            initialvalue=ds.dtype,
            parent=self,
        )
        if stype is None:
            stype = ""
        ds.scenario = scenario
        ds.dtype = stype
        self.refresh_ds()

    def del_damage_scenario(self):
        sel = self.ds_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.entry.damage_scenarios[idx]
        self.refresh_ds()

    # ------------------------------------------------------------------
    # Threat Scenarios
    # ------------------------------------------------------------------
    def add_threat_scenario(self):
        ds_sel = self.ds_tree.selection()
        if not ds_sel:
            messagebox.showwarning("Add", "Select a damage scenario first")
            return
        stride = simpledialog.askstring("Threat Scenario", "STRIDE category:", parent=self)
        if not stride:
            return
        scenario = simpledialog.askstring("Threat Scenario", "Scenario:", parent=self)
        if not scenario:
            return
        ds = self.entry.damage_scenarios[int(ds_sel[0])]
        ds.threats.append(ThreatScenario(stride, scenario))
        self.refresh_threats()

    def edit_threat_scenario(self):
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if not ds_sel or not ts_sel:
            messagebox.showwarning("Edit", "Select a threat scenario")
            return
        ds = self.entry.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        stride = simpledialog.askstring(
            "Threat Scenario", "STRIDE category:", initialvalue=ts.stride, parent=self
        )
        if not stride:
            return
        scenario = simpledialog.askstring(
            "Threat Scenario", "Scenario:", initialvalue=ts.scenario, parent=self
        )
        if not scenario:
            return
        ts.stride = stride
        ts.scenario = scenario
        self.refresh_threats()

    def del_threat_scenario(self):
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if not ds_sel or not ts_sel:
            return
        ds = self.entry.damage_scenarios[int(ds_sel[0])]
        del ds.threats[int(ts_sel[0])]
        self.refresh_threats()

    # ------------------------------------------------------------------
    # Attack Paths
    # ------------------------------------------------------------------
    def add_attack_path(self):
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if not ds_sel or not ts_sel:
            messagebox.showwarning("Add", "Select a threat scenario first")
            return
        path = simpledialog.askstring("Attack Path", "Description:", parent=self)
        if not path:
            return
        ds = self.entry.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        ts.attack_paths.append(AttackPath(path))
        self.refresh_paths()

    def edit_attack_path(self):
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        ap_sel = self.path_tree.selection()
        if not ds_sel or not ts_sel or not ap_sel:
            messagebox.showwarning("Edit", "Select an attack path")
            return
        ds = self.entry.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        ap = ts.attack_paths[int(ap_sel[0])]
        desc = simpledialog.askstring(
            "Attack Path", "Description:", initialvalue=ap.description, parent=self
        )
        if not desc:
            return
        ap.description = desc
        self.refresh_paths()

    def del_attack_path(self):
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        ap_sel = self.path_tree.selection()
        if not ds_sel or not ts_sel or not ap_sel:
            return
        ds = self.entry.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        del ts.attack_paths[int(ap_sel[0])]
        self.refresh_paths()

    # ------------------------------------------------------------------
    def apply(self):
        self.entry.asset = self.asset_var.get()
        self.entry.function = self.func_var.get()
        self.result = self.entry
