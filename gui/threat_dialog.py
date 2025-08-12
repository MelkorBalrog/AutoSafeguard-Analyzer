# Author: ChatGPT
import tkinter as tk
from tkinter import ttk, simpledialog

from gui import messagebox
from gui.toolboxes import configure_table_style
from analysis.models import (
    AttackPath,
    DamageScenario,
    FunctionThreat,
    ThreatScenario,
    ThreatEntry,
)
from sysml.sysml_repository import SysMLRepository


class ThreatDialog(simpledialog.Dialog):
    """Dialog for creating or editing a threat analysis entry."""

    def __init__(self, parent, app, entry=None):
        self.app = app
        self.entry = entry if entry else ThreatEntry("", [])
        super().__init__(parent, title="Edit Threat Entry")

    # ------------------------------------------------------------------
    def body(self, master):
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        nb = ttk.Notebook(master)
        nb.grid(row=0, column=0, sticky="nsew")

        # Asset Identification tab --------------------------------------
        asset_tab = ttk.Frame(nb)
        nb.add(asset_tab, text="Asset Identification")
        asset_tab.columnconfigure(0, weight=1)
        asset_tab.rowconfigure(2, weight=1)
        asset_tab.rowconfigure(4, weight=1)

        ai_top = ttk.Frame(asset_tab)
        ai_top.grid(row=0, column=0, sticky="ew")
        ai_top.columnconfigure(1, weight=1)
        ttk.Label(ai_top, text="Asset:").grid(row=0, column=0, sticky="w")
        self.asset_var = tk.StringVar(value=self.entry.asset)
        assets = self._get_assets(getattr(self.app.active_threat, "diagram", ""))
        self.asset_cb = ttk.Combobox(
            ai_top,
            textvariable=self.asset_var,
            values=assets,
            state="readonly",
        )
        self.asset_cb.grid(row=0, column=1, sticky="ew", padx=2)
        if self.asset_var.get() not in assets:
            self.asset_var.set("")

        func_frame = ttk.Frame(asset_tab)
        func_frame.grid(row=1, column=0, sticky="ew", pady=2)
        func_frame.columnconfigure(1, weight=1)
        ttk.Label(func_frame, text="Function:").grid(row=0, column=0, sticky="w")
        self.func_var = tk.StringVar()
        self.func_cb = ttk.Combobox(
            func_frame,
            textvariable=self.func_var,
            values=self._get_functions(),
            state="readonly",
        )
        self.func_cb.grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(func_frame, text="Add", command=self.add_function).grid(
            row=0, column=2, padx=2
        )

        configure_table_style("Threat.Functions.Treeview")
        self.func_tree = ttk.Treeview(
            asset_tab,
            columns=("function",),
            show="headings",
            style="Threat.Functions.Treeview",
        )
        self.func_tree.heading("function", text="Function")
        self.func_tree.column("function", width=680, stretch=True)
        self.func_tree.grid(row=2, column=0, sticky="nsew", padx=2)
        fscroll = ttk.Scrollbar(asset_tab, orient="vertical", command=self.func_tree.yview)
        self.func_tree.configure(yscrollcommand=fscroll.set)
        fscroll.grid(row=2, column=1, sticky="ns")
        self.func_tree.bind("<<TreeviewSelect>>", self.on_func_select)
        ttk.Button(asset_tab, text="Remove Function", command=self.remove_function).grid(
            row=3, column=0, sticky="w", padx=2, pady=2
        )
        for fn in self.entry.functions:
            self.func_tree.insert("", tk.END, values=(fn.name,))
        if self.entry.functions:
            first = self.func_tree.get_children()[0]
            self.func_tree.selection_set(first)
            self.func_tree.focus(first)

        ds_frame = ttk.Frame(asset_tab)
        ds_frame.grid(row=4, column=0, sticky="nsew")
        configure_table_style("Threat.Damage.Treeview")
        self.ds_tree = ttk.Treeview(
            ds_frame,
            columns=("scenario", "type"),
            show="headings",
            style="Threat.Damage.Treeview",
        )
        self.ds_tree.heading("scenario", text="Damage Scenario")
        self.ds_tree.heading("type", text="Type")
        self.ds_tree.column("scenario", width=560, stretch=True)
        self.ds_tree.column("type", width=120, stretch=True)
        self.ds_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ds_scroll = ttk.Scrollbar(ds_frame, orient="vertical", command=self.ds_tree.yview)
        self.ds_tree.configure(yscrollcommand=ds_scroll.set)
        ds_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ds_tree.bind("<<TreeviewSelect>>", self.on_ds_select)

        ds_edit = ttk.Frame(asset_tab)
        ds_edit.grid(row=5, column=0, sticky="ew", pady=2)
        ds_edit.columnconfigure(1, weight=1)
        ds_edit.columnconfigure(3, weight=1)
        ttk.Label(ds_edit, text="Damage Scenario:").grid(row=0, column=0, sticky="w")
        self.ds_scenario_var = tk.StringVar()
        ttk.Entry(ds_edit, textvariable=self.ds_scenario_var).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Label(ds_edit, text="Type:").grid(row=0, column=2, sticky="w")
        self.ds_type_var = tk.StringVar()
        self.ds_type_cb = ttk.Combobox(
            ds_edit,
            textvariable=self.ds_type_var,
            values=["Confidentiality", "Integrity", "Availability"],
            state="readonly",
        )
        self.ds_type_cb.grid(row=0, column=3, sticky="ew", padx=2)

        ds_btn = ttk.Frame(asset_tab)
        ds_btn.grid(row=6, column=0, sticky="ew")
        ttk.Button(ds_btn, text="Add", command=self.add_damage_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ds_btn, text="Update", command=self.update_damage_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ds_btn, text="Delete", command=self.del_damage_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )

        # Threat Analysis tab -------------------------------------------
        threat_tab = ttk.Frame(nb)
        nb.add(threat_tab, text="Threat Analysis")
        threat_tab.columnconfigure(0, weight=1)
        threat_tab.rowconfigure(0, weight=1)

        ta_frame = ttk.Frame(threat_tab)
        ta_frame.grid(row=0, column=0, sticky="nsew")
        ta_frame.columnconfigure(0, weight=1)
        ta_frame.rowconfigure(0, weight=1)
        ta_frame.rowconfigure(1, weight=1)
        configure_table_style("Threat.Scenarios.Treeview")
        self.threat_tree = ttk.Treeview(
            ta_frame,
            columns=("stride", "scenario"),
            show="headings",
            style="Threat.Scenarios.Treeview",
        )
        self.threat_tree.heading("stride", text="STRIDE")
        self.threat_tree.heading("scenario", text="Threat Scenario")
        self.threat_tree.column("stride", width=120, stretch=True)
        self.threat_tree.column("scenario", width=560, stretch=True)
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
        )
        self.path_tree.heading("path", text="Attack Path")
        self.path_tree.column("path", width=680, stretch=True)
        self.path_tree.grid(row=1, column=0, sticky="nsew")
        pscroll = ttk.Scrollbar(ta_frame, orient="vertical", command=self.path_tree.yview)
        self.path_tree.configure(yscrollcommand=pscroll.set)
        pscroll.grid(row=1, column=1, sticky="ns")
        self.path_tree.bind("<<TreeviewSelect>>", self.on_path_select)

        ts_edit = ttk.Frame(threat_tab)
        ts_edit.grid(row=1, column=0, sticky="ew", pady=2)
        ts_edit.columnconfigure(1, weight=1)
        ts_edit.columnconfigure(3, weight=1)
        ttk.Label(ts_edit, text="STRIDE:").grid(row=0, column=0, sticky="w")
        self.threat_stride_var = tk.StringVar()
        self.threat_stride_cb = ttk.Combobox(
            ts_edit,
            textvariable=self.threat_stride_var,
            values=[
                "Spoofing",
                "Tampering",
                "Repudiation",
                "Information disclosure",
                "Denial of service",
                "Elevation of privilege",
            ],
            state="readonly",
        )
        self.threat_stride_cb.grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Label(ts_edit, text="Threat Scenario:").grid(row=0, column=2, sticky="w")
        self.threat_scenario_var = tk.StringVar()
        ttk.Entry(ts_edit, textvariable=self.threat_scenario_var).grid(
            row=0, column=3, sticky="ew", padx=2
        )

        ts_btn = ttk.Frame(threat_tab)
        ts_btn.grid(row=2, column=0, sticky="ew")
        ttk.Button(ts_btn, text="Add", command=self.add_threat_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ts_btn, text="Update", command=self.update_threat_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(ts_btn, text="Delete", command=self.del_threat_scenario).pack(
            side=tk.LEFT, padx=2, pady=2
        )

        path_edit = ttk.Frame(threat_tab)
        path_edit.grid(row=3, column=0, sticky="ew", pady=2)
        path_edit.columnconfigure(1, weight=1)
        ttk.Label(path_edit, text="Attack Path:").grid(row=0, column=0, sticky="w")
        self.path_var = tk.StringVar()
        ttk.Entry(path_edit, textvariable=self.path_var).grid(
            row=0, column=1, sticky="ew", padx=2
        )

        path_btn = ttk.Frame(threat_tab)
        path_btn.grid(row=4, column=0, sticky="ew")
        ttk.Button(path_btn, text="Add", command=self.add_attack_path).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(path_btn, text="Update", command=self.update_attack_path).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(path_btn, text="Delete", command=self.del_attack_path).pack(
            side=tk.LEFT, padx=2, pady=2
        )

        self.refresh_ds()
        return nb


    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def _get_assets(self, diag_id):
        repo = SysMLRepository.get_instance()
        names = set()
        diag = repo.diagrams.get(diag_id) if diag_id else None
        if diag:
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
            for conn in getattr(diag, "connections", []):
                name = conn.get("name")
                if name:
                    names.add(name)
        return sorted(names)

    def _get_functions(self):
        return self.app.get_all_action_names()

    # ------------------------------------------------------------------
    # Function helpers
    # ------------------------------------------------------------------
    def _selected_func_idx(self):
        sel = self.func_tree.selection()
        return self.func_tree.index(sel[0]) if sel else None

    def add_function(self):
        func = self.func_var.get()
        existing = [self.func_tree.item(iid, "values")[0] for iid in self.func_tree.get_children()]
        if func and func not in existing:
            self.entry.functions.append(FunctionThreat(func))
            item = self.func_tree.insert("", tk.END, values=(func,))
            self.func_tree.selection_set(item)
            self.func_tree.focus(item)
            self.on_func_select()
        self.func_var.set("")

    def remove_function(self):
        sel = self.func_tree.selection()
        if sel:
            idx = self.func_tree.index(sel[0])
            self.func_tree.delete(sel[0])
            del self.entry.functions[idx]
            self.refresh_ds()

    def on_func_select(self, *_):
        self.refresh_ds()

    # ------------------------------------------------------------------
    def on_ds_select(self, *_):
        func_idx = self._selected_func_idx()
        sel = self.ds_tree.selection()
        if func_idx is not None and sel:
            func = self.entry.functions[func_idx]
            ds = func.damage_scenarios[int(sel[0])]
            self.ds_scenario_var.set(ds.scenario)
            self.ds_type_var.set(ds.dtype)
        else:
            self.ds_scenario_var.set("")
            self.ds_type_var.set("")
        self.refresh_threats()

    def on_threat_select(self, *_):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        sel = self.threat_tree.selection()
        if func_idx is not None and ds_sel and sel:
            func = self.entry.functions[func_idx]
            ds = func.damage_scenarios[int(ds_sel[0])]
            ts = ds.threats[int(sel[0])]
            self.threat_stride_var.set(ts.stride)
            self.threat_scenario_var.set(ts.scenario)
        else:
            self.threat_stride_var.set("")
            self.threat_scenario_var.set("")
        self.refresh_paths()

    def on_path_select(self, *_):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        ap_sel = self.path_tree.selection()
        if func_idx is not None and ds_sel and ts_sel and ap_sel:
            func = self.entry.functions[func_idx]
            ds = func.damage_scenarios[int(ds_sel[0])]
            ts = ds.threats[int(ts_sel[0])]
            ap = ts.attack_paths[int(ap_sel[0])]
            self.path_var.set(ap.description)
        else:
            self.path_var.set("")

    def refresh_ds(self):
        self.ds_tree.delete(*self.ds_tree.get_children())
        func_idx = self._selected_func_idx()
        if func_idx is None:
            self.on_ds_select()
            return
        func = self.entry.functions[func_idx]
        for idx, ds in enumerate(func.damage_scenarios):
            self.ds_tree.insert("", "end", iid=str(idx), values=(ds.scenario, ds.dtype))
        self.on_ds_select()

    def refresh_threats(self):
        self.threat_tree.delete(*self.threat_tree.get_children())
        self.path_tree.delete(*self.path_tree.get_children())
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        if func_idx is None or not ds_sel:
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        for idx, ts in enumerate(ds.threats):
            self.threat_tree.insert("", "end", iid=str(idx), values=(ts.stride, ts.scenario))
        self.on_threat_select()

    def refresh_paths(self):
        self.path_tree.delete(*self.path_tree.get_children())
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if func_idx is None or not ds_sel or not ts_sel:
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        for idx, ap in enumerate(ts.attack_paths):
            self.path_tree.insert("", "end", iid=str(idx), values=(ap.description,))
        self.on_path_select()

    # ------------------------------------------------------------------
    # Damage Scenarios
    # ------------------------------------------------------------------
    def add_damage_scenario(self):
        func_idx = self._selected_func_idx()
        if func_idx is None:
            messagebox.showwarning("Add", "Select a function first")
            return
        scenario = self.ds_scenario_var.get().strip()
        if not scenario:
            messagebox.showwarning("Add", "Enter a damage scenario")
            return
        stype = self.ds_type_var.get().strip()
        func = self.entry.functions[func_idx]
        func.damage_scenarios.append(DamageScenario(scenario, stype))
        self.ds_scenario_var.set("")
        self.ds_type_var.set("")
        self.refresh_ds()

    def update_damage_scenario(self):
        func_idx = self._selected_func_idx()
        sel = self.ds_tree.selection()
        if func_idx is None or not sel:
            messagebox.showwarning("Update", "Select a damage scenario")
            return
        idx = int(sel[0])
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[idx]
        ds.scenario = self.ds_scenario_var.get()
        ds.dtype = self.ds_type_var.get()
        self.refresh_ds()

    def del_damage_scenario(self):
        func_idx = self._selected_func_idx()
        sel = self.ds_tree.selection()
        if func_idx is None or not sel:
            return
        idx = int(sel[0])
        func = self.entry.functions[func_idx]
        del func.damage_scenarios[idx]
        self.refresh_ds()
        self.ds_scenario_var.set("")
        self.ds_type_var.set("")

    # ------------------------------------------------------------------
    # Threat Scenarios
    # ------------------------------------------------------------------
    def add_threat_scenario(self):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        if func_idx is None or not ds_sel:
            messagebox.showwarning("Add", "Select a damage scenario first")
            return
        stride = self.threat_stride_var.get().strip()
        scenario = self.threat_scenario_var.get().strip()
        if not stride or not scenario:
            messagebox.showwarning("Add", "Enter STRIDE and scenario")
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        ds.threats.append(ThreatScenario(stride, scenario))
        self.threat_stride_var.set("")
        self.threat_scenario_var.set("")
        self.refresh_threats()

    def update_threat_scenario(self):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if func_idx is None or not ds_sel or not ts_sel:
            messagebox.showwarning("Update", "Select a threat scenario")
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        ts.stride = self.threat_stride_var.get()
        ts.scenario = self.threat_scenario_var.get()
        self.refresh_threats()

    def del_threat_scenario(self):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if func_idx is None or not ds_sel or not ts_sel:
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        del ds.threats[int(ts_sel[0])]
        self.refresh_threats()
        self.threat_stride_var.set("")
        self.threat_scenario_var.set("")

    # ------------------------------------------------------------------
    # Attack Paths
    # ------------------------------------------------------------------
    def add_attack_path(self):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        if func_idx is None or not ds_sel or not ts_sel:
            messagebox.showwarning("Add", "Select a threat scenario first")
            return
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("Add", "Enter an attack path")
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        ts.attack_paths.append(AttackPath(path))
        self.path_var.set("")
        self.refresh_paths()

    def update_attack_path(self):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        ap_sel = self.path_tree.selection()
        if func_idx is None or not ds_sel or not ts_sel or not ap_sel:
            messagebox.showwarning("Update", "Select an attack path")
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        ap = ts.attack_paths[int(ap_sel[0])]
        ap.description = self.path_var.get()
        self.refresh_paths()

    def del_attack_path(self):
        func_idx = self._selected_func_idx()
        ds_sel = self.ds_tree.selection()
        ts_sel = self.threat_tree.selection()
        ap_sel = self.path_tree.selection()
        if func_idx is None or not ds_sel or not ts_sel or not ap_sel:
            return
        func = self.entry.functions[func_idx]
        ds = func.damage_scenarios[int(ds_sel[0])]
        ts = ds.threats[int(ts_sel[0])]
        del ts.attack_paths[int(ap_sel[0])]
        self.refresh_paths()
        self.path_var.set("")

    # ------------------------------------------------------------------
    def apply(self):
        self.entry.asset = self.asset_var.get()
        self.result = self.entry

    # ------------------------------------------------------------------
    def buttonbox(self):
        """Add explicit OK/Cancel buttons and set dialog size."""
        box = ttk.Frame(self)
        box.pack(fill="x", padx=5, pady=5)

        ok_btn = ttk.Button(
            box, text="OK", width=10, command=self.ok, default=tk.ACTIVE
        )
        ok_btn.pack(side=tk.RIGHT, padx=5)
        cancel_btn = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        ok_btn.focus_set()
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        # Resize after layout so width/height are accurate
        self.after_idle(self._set_initial_size)

    def _set_initial_size(self):
        """Shrink dialog while ensuring controls remain visible."""
        self.update_idletasks()
        width = max(self.winfo_width(), self.winfo_reqwidth(), 800)
        height = max(self.winfo_height() // 2, 600)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
