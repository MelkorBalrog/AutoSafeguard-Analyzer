# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import csv
import copy
import textwrap
from analysis.models import (
    ReliabilityComponent,
    ReliabilityAnalysis,
    HazopEntry,
    HaraEntry,
    HazopDoc,
    HaraDoc,
    FI2TCDoc,
    TC2FIDoc,
    QUALIFICATIONS,
    COMPONENT_ATTR_TEMPLATES,
    RELIABILITY_MODELS,
    PASSIVE_QUAL_FACTORS,
    component_fit_map,
    calc_asil,
)
from analysis.fmeda_utils import compute_fmeda_metrics
from analysis.constants import CHECK_MARK, CROSS_MARK


def _total_fit_from_boms(boms):
    """Return the aggregated FIT of all components in ``boms``.

    Each element of ``boms`` is a list of :class:`ReliabilityComponent` objects.
    The stored ``fit`` values of the components are used so pre-calculated
    analyses can be combined without a mission profile.
    """

    total = 0.0
    for bom in boms:
        total += sum(component_fit_map(bom).values())
    return total

def _wrap_val(val, width=30):
    """Return text wrapped value for tree view cells."""
    if val is None:
        return ""
    return textwrap.fill(str(val), width)

class ReliabilityWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("Reliability Analysis")
        self.geometry("600x400")
        self.components = []

        ttk.Label(self, text="Standard:").pack(anchor="w")
        self.standard_var = tk.StringVar(value="IEC 62380")
        ttk.Combobox(
            self,
            textvariable=self.standard_var,
            values=["IEC 62380", "SN 29500"],
            state="readonly",
        ).pack(anchor="w")

        ttk.Label(self, text="Mission Profile:").pack(anchor="w")
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            self,
            textvariable=self.profile_var,
            values=[mp.name for mp in app.mission_profiles],
            state="readonly",
        )
        self.profile_combo.pack(anchor="w", fill="x")

        ttk.Label(self, text="Analysis:").pack(anchor="w")
        self.analysis_var = tk.StringVar()
        self.analysis_combo = ttk.Combobox(
            self,
            textvariable=self.analysis_var,
            state="readonly",
        )
        self.analysis_combo.pack(anchor="w", fill="x")
        self.analysis_combo.bind("<<ComboboxSelected>>", self.load_selected_analysis)
        self.refresh_analysis_list()

        self.tree = ttk.Treeview(
            self,
            columns=("name", "type", "qty", "fit", "qualification"),
            show="headings",
        )
        for col in ("name", "type", "qty", "fit", "qualification"):
            heading = "Qualification" if col == "qualification" else col.capitalize()
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=120 if col == "qualification" else 100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.show_formula)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Load CSV", command=self.load_csv).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Add Component", command=self.add_component).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Add Circuit", command=self.add_circuit).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Configure Component", command=self.configure_component).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Calculate FIT", command=self.calculate_fit).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Save Analysis", command=self.save_analysis).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Load Analysis", command=self.load_analysis).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Delete Analysis", command=self.delete_analysis).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        self.formula_label = ttk.Label(self, text="")
        self.formula_label.pack(anchor="w", padx=5, pady=5)

    def add_component(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Component")
        ttk.Label(dialog, text="Name").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Type").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        type_var = tk.StringVar(value="capacitor")
        type_cb = ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=list(COMPONENT_ATTR_TEMPLATES.keys()),
            state="readonly",
        )
        type_cb.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Quantity").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        qty_var = tk.IntVar(value=1)
        ttk.Entry(dialog, textvariable=qty_var).grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Qualification").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        qual_var = tk.StringVar(value="None")
        ttk.Combobox(dialog, textvariable=qual_var, values=QUALIFICATIONS, state="readonly").grid(row=3, column=1, padx=5, pady=5)
        passive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Passive", variable=passive_var).grid(row=4, column=0, columnspan=2, pady=5)

        attr_frame = ttk.Frame(dialog)
        attr_frame.grid(row=5, column=0, columnspan=2)
        attr_vars = {}

        def refresh_attr_fields(*_):
            for child in attr_frame.winfo_children():
                child.destroy()
            attr_vars.clear()
            template = COMPONENT_ATTR_TEMPLATES.get(type_var.get(), {})
            for i, (k, v) in enumerate(template.items()):
                ttk.Label(attr_frame, text=k).grid(row=i, column=0, padx=5, pady=5, sticky="e")
                if isinstance(v, list):
                    var = tk.StringVar(value=v[0])
                    ttk.Combobox(attr_frame, textvariable=var, values=v, state="readonly").grid(row=i, column=1, padx=5, pady=5)
                else:
                    var = tk.StringVar(value=str(v))
                    ttk.Entry(attr_frame, textvariable=var).grid(row=i, column=1, padx=5, pady=5)
                attr_vars[k] = var

        type_cb.bind("<<ComboboxSelected>>", refresh_attr_fields)
        refresh_attr_fields()

        def ok():
            comp = ReliabilityComponent(
                name_var.get(),
                type_var.get(),
                qty_var.get(),
                {},
                qual_var.get(),
                is_passive=passive_var.get(),
            )
            for k, var in attr_vars.items():
                comp.attributes[k] = var.get()
            self.components.append(comp)
            self.refresh_tree()
            dialog.destroy()

        ttk.Button(dialog, text="Add", command=ok).grid(row=6, column=0, columnspan=2, pady=5)
        dialog.grab_set()
        dialog.wait_window()

    def add_circuit(self):
        dlg = tk.Toplevel(self)
        dlg.title("New Circuit")
        ttk.Label(dlg, text="Name").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_var = tk.StringVar()
        ttk.Entry(dlg, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(dlg, text="BOMs").grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        lb = tk.Listbox(dlg, selectmode=tk.MULTIPLE, height=6)
        for ra in self.app.reliability_analyses:
            lb.insert(tk.END, ra.name)
        lb.grid(row=1, column=1, padx=5, pady=5)
        qty_var = tk.IntVar(value=1)
        ttk.Label(dlg, text="Quantity").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(dlg, textvariable=qty_var).grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(dlg, text="Qualification").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        qual_var = tk.StringVar(value="None")
        ttk.Combobox(dlg, textvariable=qual_var, values=QUALIFICATIONS, state="readonly").grid(row=3, column=1, padx=5, pady=5)
        passive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dlg, text="Passive", variable=passive_var).grid(row=4, column=0, columnspan=2, pady=5)

        def ok():
            bom_idxs = lb.curselection()
            boms = [self.app.reliability_analyses[i].components for i in bom_idxs]
            comp = ReliabilityComponent(
                name_var.get(),
                "circuit",
                qty_var.get(),
                {},
                qual_var.get(),
                is_passive=passive_var.get(),
            )
            comp.sub_boms = copy.deepcopy(boms)
            comp.fit = 0.0
            self.components.append(comp)
            self.refresh_tree()
            dlg.destroy()

        ttk.Button(dlg, text="Add", command=ok).grid(row=5, column=0, columnspan=2, pady=5)
        dlg.grab_set()
        dlg.wait_window()

    def show_formula(self, event=None):
        sel = self.tree.focus()
        if not sel:
            self.formula_label.config(text="")
            return
        idx = self.tree.index(sel)
        if idx >= len(self.components):
            return
        comp = self.components[idx]
        std = self.standard_var.get()
        info = RELIABILITY_MODELS.get(std, {}).get(comp.comp_type)
        if info:
            self.formula_label.config(text=f"Formula: {info['text']}")
        else:
            self.formula_label.config(text="Formula: N/A")

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for comp in self.components:
            self.tree.insert(
                "",
                "end",
                values=(
                    comp.name,
                    comp.comp_type,
                    comp.quantity,
                    f"{comp.fit:.2f}",
                    comp.qualification,
                ),
            )
        self.profile_combo.config(values=[mp.name for mp in self.app.mission_profiles])
        # keep application level components updated so property dialogs see them
        self.app.reliability_components = list(self.components)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        self.components.clear()
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            mapping = self.ask_mapping(fields)
            if not mapping:
                return
            for row in reader:
                try:
                    name = row.get(mapping["name"], "")
                    ctype = row.get(mapping["type"], "")
                    qty = int(row.get(mapping["qty"], 1) or 1)
                    qual = row.get(mapping.get("qualification"), "") if mapping.get("qualification") else ""
                    comp = ReliabilityComponent(name, ctype, qty, {}, qual)
                    template = COMPONENT_ATTR_TEMPLATES.get(ctype, {})
                    for k, v in template.items():
                        comp.attributes[k] = v[0] if isinstance(v, list) else v
                    # store any extra columns as attributes
                    for key, val in row.items():
                        if key not in mapping.values():
                            comp.attributes[key] = val
                    self.components.append(comp)
                except Exception:
                    continue
        self.refresh_tree()

    def ask_mapping(self, fields):
        if not fields:
            return None
        win = tk.Toplevel(self)
        win.title("Map Columns")
        vars = {}
        targets = ["name", "type", "qty", "qualification"]
        for i, tgt in enumerate(targets):
            ttk.Label(win, text=tgt.capitalize()).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            var = tk.StringVar()
            cb = ttk.Combobox(win, textvariable=var, values=fields, state="readonly")
            if i < len(fields):
                var.set(fields[i])
            cb.grid(row=i, column=1, padx=5, pady=5)
            vars[tgt] = var

        result = {}

        def ok():
            for k, v in vars.items():
                result[k] = v.get()
            win.destroy()

        def cancel():
            result.clear()
            win.destroy()

        ttk.Button(win, text="OK", command=ok).grid(row=len(targets), column=0, pady=5)
        ttk.Button(win, text="Cancel", command=cancel).grid(row=len(targets), column=1, pady=5)
        win.grab_set()
        win.wait_window()
        if not result:
            return None
        return result

    def configure_component(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Configure", "Select a component")
            return
        idx = self.tree.index(sel)
        comp = self.components[idx]

        template = COMPONENT_ATTR_TEMPLATES.get(comp.comp_type, {})
        for k, v in template.items():
            comp.attributes.setdefault(k, v[0] if isinstance(v, list) else v)

        class ParamDialog(simpledialog.Dialog):
            def body(self, master):
                self.resizable(False, False)
                self.vars = {}
                nb = ttk.Notebook(master)
                nb.pack(fill=tk.BOTH, expand=True)
                gen_tab = ttk.Frame(nb)
                attr_tab = ttk.Frame(nb)
                nb.add(gen_tab, text="General")
                nb.add(attr_tab, text="Attributes")

                row = 0
                ttk.Label(gen_tab, text="Quantity").grid(row=row, column=0, padx=5, pady=5, sticky="e")
                qty_var = tk.IntVar(value=comp.quantity)
                ttk.Entry(gen_tab, textvariable=qty_var).grid(row=row, column=1, padx=5, pady=5)
                self.vars["__qty__"] = qty_var
                row += 1
                ttk.Label(gen_tab, text="Qualification").grid(row=row, column=0, padx=5, pady=5, sticky="e")
                qual_var = tk.StringVar(value=comp.qualification)
                ttk.Combobox(gen_tab, textvariable=qual_var, values=QUALIFICATIONS, state="readonly").grid(row=row, column=1, padx=5, pady=5)
                self.vars["__qual__"] = qual_var

                row = 0
                for k, v in comp.attributes.items():
                    ttk.Label(attr_tab, text=k).grid(row=row, column=0, padx=5, pady=5, sticky="e")
                    if isinstance(template.get(k), list):
                        var = tk.StringVar(value=str(v))
                        ttk.Combobox(attr_tab, textvariable=var, values=template[k], state="readonly").grid(row=row, column=1, padx=5, pady=5)
                    else:
                        var = tk.StringVar(value=str(v))
                        ttk.Entry(attr_tab, textvariable=var).grid(row=row, column=1, padx=5, pady=5)
                    self.vars[k] = var
                    row += 1

            def apply(self):
                comp.quantity = int(self.vars["__qty__"].get())
                comp.qualification = self.vars["__qual__"].get()
                for k, v in self.vars.items():
                    if k.startswith("__"):
                        continue
                    comp.attributes[k] = v.get()

        ParamDialog(self)
        self.refresh_tree()

    def calculate_fit(self):
        prof_name = self.profile_var.get()
        mp = next((m for m in self.app.mission_profiles if m.name == prof_name), None)
        needs_profile = any(not c.sub_boms for c in self.components)
        if mp is None and needs_profile:
            messagebox.showwarning("FIT", "Select a mission profile")
            return
        std = self.standard_var.get()
        total = 0.0
        for comp in self.components:
            if comp.sub_boms:
                # Aggregate FIT from the referenced BOMs without recomputation
                comp.fit = _total_fit_from_boms(comp.sub_boms)
            else:
                info = RELIABILITY_MODELS.get(std, {}).get(comp.comp_type)
                if info:
                    qf = PASSIVE_QUAL_FACTORS.get(comp.qualification, 1.0) if comp.is_passive else 1.0
                    if mp is not None:
                        comp.fit = info["formula"](comp.attributes, mp) * mp.tau * qf
                    else:
                        comp.fit = 0.0
                else:
                    comp.fit = 0.0
            total += comp.fit * comp.quantity

        sg_targets = {sg.user_name: {
            "dc": getattr(sg, "sg_dc_target", 0.0),
            "spfm": getattr(sg, "sg_spfm_target", 0.0),
            "lpfm": getattr(sg, "sg_lpfm_target", 0.0),
        } for sg in self.app.top_events}
        for be in self.app.fmea_entries:
            sg = getattr(be, "fmeda_safety_goal", "")
            if sg and sg not in sg_targets:
                sg_targets[sg] = {
                    "dc": getattr(be, "fmeda_dc_target", 0.0),
                    "spfm": getattr(be, "fmeda_spfm_target", 0.0),
                    "lpfm": getattr(be, "fmeda_lpfm_target", 0.0),
                }

        metrics = compute_fmeda_metrics(
            self.app.fmea_entries,
            self.components,
            self.app.get_safety_goal_asil,
            sg_targets=sg_targets,
        )
        self.app.reliability_components = list(self.components)
        self.app.reliability_total_fit = metrics["total"]
        self.app.spfm = metrics["spfm_raw"]
        self.app.lpfm = metrics["lpfm_raw"]
        self.app.reliability_dc = metrics["dc"]
        self.refresh_tree()
        goal_res = []
        for sg, gm in metrics.get("goal_metrics", {}).items():
            ok = gm["ok_dc"] and gm["ok_spfm"] and gm["ok_lpfm"]
            symbol = CHECK_MARK if ok else CROSS_MARK
            goal_res.append(f"{sg}:{symbol}")
        extra = f"  [{' ; '.join(goal_res)}]" if goal_res else ""
        self.formula_label.config(
            text=(
                f"Total FIT: {metrics['total']:.2f}  DC: {metrics['dc']:.2f}  "
                f"SPFM: {metrics['spfm_raw']:.2f}  LPFM: {metrics['lpfm_raw']:.2f}" + extra
            )
        )

    def save_analysis(self):
        if not self.components:
            messagebox.showwarning("Save", "No components defined")
            return
        name = simpledialog.askstring("Save Analysis", "Enter analysis name:")
        if not name:
            return
        ra = ReliabilityAnalysis(
            name,
            self.standard_var.get(),
            self.profile_var.get(),
            copy.deepcopy(self.components),
            self.app.reliability_total_fit,
            self.app.spfm,
            self.app.lpfm,
            self.app.reliability_dc,
        )
        self.app.reliability_analyses.append(ra)
        self.refresh_analysis_list()
        self.analysis_var.set(name)
        messagebox.showinfo("Save", "Analysis saved")

    def load_analysis(self):
        """Load a previously saved reliability analysis."""
        if not self.app.reliability_analyses:
            messagebox.showwarning("Load", "No saved analyses")
            return
        win = tk.Toplevel(self)
        win.title("Select Analysis")
        lb = tk.Listbox(win, height=8, width=40)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for ra in self.app.reliability_analyses:
            lb.insert(tk.END, ra.name)

        def do_load():
            sel = lb.curselection()
            if not sel:
                return
            ra = self.app.reliability_analyses[sel[0]]
            self.standard_var.set(ra.standard)
            self.profile_var.set(ra.profile)
            self.components = copy.deepcopy(ra.components)
            self.app.reliability_total_fit = ra.total_fit
            self.app.spfm = ra.spfm
            self.app.lpfm = ra.lpfm
            self.app.reliability_dc = ra.dc
            win.destroy()
            self.refresh_tree()
            self.formula_label.config(
                text=f"Total FIT: {ra.total_fit:.2f}  DC: {ra.dc:.2f}  SPFM: {ra.spfm:.2f}  LPFM: {ra.lpfm:.2f}"
            )

        ttk.Button(win, text="Load", command=do_load).pack(side=tk.RIGHT, padx=5, pady=5)

    def load_selected_analysis(self, *_):
        """Load analysis chosen from the combo box."""
        name = self.analysis_var.get()
        ra = next((r for r in self.app.reliability_analyses if r.name == name), None)
        if ra:
            self._populate_from_analysis(ra)

    def delete_analysis(self):
        name = self.analysis_var.get()
        if not name:
            messagebox.showwarning("Delete", "Select an analysis")
            return
        if not messagebox.askyesno("Delete", f"Delete analysis '{name}'?"):
            return
        self.app.reliability_analyses = [r for r in self.app.reliability_analyses if r.name != name]
        self.analysis_var.set("")
        self.refresh_analysis_list()
        self.components.clear()
        self.refresh_tree()
        self.formula_label.config(text="")

    def refresh_analysis_list(self):
        names = [ra.name for ra in self.app.reliability_analyses]
        self.analysis_combo.configure(values=names)

    def _populate_from_analysis(self, ra):
        self.standard_var.set(ra.standard)
        self.profile_var.set(ra.profile)
        self.components = copy.deepcopy(ra.components)
        self.app.reliability_total_fit = ra.total_fit
        self.app.spfm = ra.spfm
        self.app.lpfm = ra.lpfm
        self.app.reliability_dc = ra.dc
        self.refresh_tree()
        self.formula_label.config(
            text=f"Total FIT: {ra.total_fit:.2f}  DC: {ra.dc:.2f}  SPFM: {ra.spfm:.2f}  LPFM: {ra.lpfm:.2f}"
        )


class FI2TCWindow(tk.Frame):
    COLS = [
        "id","system_function","allocation","interfaces","insufficiency",
        "scene","scenario","driver_behavior","occurrence","vehicle_effect",
        "severity","design_measures","verification","measure_effectiveness",
        "triggering_condition","worst_case","tc_effect","mitigation","acceptance"
    ]
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("FI2TC Analysis")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="FI2TC:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        style = ttk.Style(self)
        style.configure("FI2TC.Treeview", rowheight=80)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.COLS,
            show="headings",
            style="FI2TC.Treeview",
            height=4,
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in self.COLS:
            self.tree.heading(c, text=c.replace("_"," ").title())
            width = 200 if c == "hazard" else 120
            self.tree.column(c, width=width)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self.edit_row())
        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text="Add", command=self.add_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Edit", command=self.edit_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Delete", command=self.del_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2, pady=2)
        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.fi2tc_entries:
            vals = [_wrap_val(row.get(k, "")) for k in self.COLS]
            self.tree.insert("", "end", values=vals)

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, app, data=None):
            self.app = app
            self.parent_win = parent
            default = {k: "" for k in parent.COLS}
            self.data = data or default
            super().__init__(parent, title="Edit Row")
        def body(self, master):
            fi_names = [n.user_name or f"FI {n.unique_id}" for n in self.app.get_all_functional_insufficiencies()]
            tc_names = [n.user_name or f"TC {n.unique_id}" for n in self.app.get_all_triggering_conditions()]
            func_names = self.app.get_all_function_names()
            comp_names = self.app.get_all_component_names()
            scen_names = self.app.get_all_scenario_names()
            scene_names = self.app.get_all_scenery_names()
            self.widgets = {}
            r = 0

            def refresh_funcs(*_):
                comp = self.widgets.get("allocation")
                if isinstance(comp, tk.StringVar):
                    func_opts = sorted({e.function for e in self.app.hazop_entries if not comp.get() or e.component == comp.get()})
                else:
                    func_opts = func_names
                if "system_function" in self.widgets:
                    w = self.widgets["system_function_widget"]
                    w["values"] = func_opts

            for col in self.parent_win.COLS:
                ttk.Label(master, text=col.replace("_", " ").title()).grid(row=r, column=0, sticky="e", padx=5, pady=2)
                if col == "triggering_condition":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=tc_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "insufficiency":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=fi_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "system_function":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=func_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                    self.widgets["system_function_widget"] = cb
                elif col == "allocation":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=comp_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    cb.bind("<<ComboboxSelected>>", refresh_funcs)
                    self.widgets[col] = var
                elif col == "scene":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=scene_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "scenario":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=scen_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "severity":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=["1", "2", "3"], state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                else:
                    txt = tk.Text(master, width=25, height=2, wrap="word")
                    txt.insert("1.0", self.data.get(col, ""))
                    txt.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = txt
                r += 1
            refresh_funcs()
            
        def apply(self):
            for col, widget in self.widgets.items():
                if isinstance(widget, tk.Entry):
                    self.data[col] = widget.get()
                elif isinstance(widget, tk.Text):
                    self.data[col] = widget.get("1.0", "end-1c")
                else:
                    self.data[col] = widget.get()
            self.result = True

    def add_row(self):
        dlg = self.RowDialog(self, self.app)
        if getattr(dlg, "result", None):
            self.app.fi2tc_entries.append(dlg.data)
            self.refresh()
    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        data = self.app.fi2tc_entries[idx]
        dlg = self.RowDialog(self, self.app, data)
        if getattr(dlg, "result", None):
            self.refresh()
    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.fi2tc_entries):
                del self.app.fi2tc_entries[idx]
        self.refresh()
    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(self.COLS)
            for r in self.app.fi2tc_entries:
                w.writerow([r.get(k, "") for k in self.COLS])
        messagebox.showinfo("Export", "FI2TC exported")

    def refresh_docs(self):
        names = [d.name for d in self.app.fi2tc_docs]
        self.doc_cb.configure(values=names)
        if self.app.active_fi2tc:
            self.doc_var.set(self.app.active_fi2tc.name)
        elif names:
            self.doc_var.set(names[0])

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.fi2tc_docs:
            if d.name == name:
                self.app.active_fi2tc = d
                self.app.fi2tc_entries = d.entries
                break
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New FI2TC", "Name:")
        if not name:
            return
        doc = FI2TCDoc(name, [])
        self.app.fi2tc_docs.append(doc)
        self.app.active_fi2tc = doc
        self.app.fi2tc_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_fi2tc:
            return
        name = simpledialog.askstring(
            "Rename FI2TC", "Name:", initialvalue=self.app.active_fi2tc.name
        )
        if not name:
            return
        self.app.active_fi2tc.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_fi2tc
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete FI2TC '{doc.name}'?"):
            return
        self.app.fi2tc_docs.remove(doc)
        if self.app.fi2tc_docs:
            self.app.active_fi2tc = self.app.fi2tc_docs[0]
        else:
            self.app.active_fi2tc = None
        self.app.fi2tc_entries = (
            self.app.active_fi2tc.entries if self.app.active_fi2tc else []
        )
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

class HazopWindow(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("HAZOP Analysis")
            master.geometry("600x400")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="HAZOP:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        columns = ("function", "malfunction", "type", "safety", "rationale")
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(content, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            if col in ("rationale", "hazard"):
                width = 200
            else:
                width = 120
            self.tree.column(col, width=width)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.explorer = ttk.Frame(content)
        self.explorer.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Label(self.explorer, text="Malfunction Explorer").pack()
        self.mal_list = tk.Listbox(self.explorer, height=10)
        self.mal_list.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.update_mal_explorer)

        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text="Add", command=self.add_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Edit", command=self.edit_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Delete", command=self.del_row).pack(side=tk.LEFT, padx=2, pady=2)

        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh_docs(self):
        names = [d.name for d in self.app.hazop_docs]
        self.doc_cb["values"] = names
        if self.app.active_hazop:
            self.doc_var.set(self.app.active_hazop.name)
        elif names:
            self.doc_var.set(names[0])

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.hazop_docs:
            if d.name == name:
                self.app.active_hazop = d
                self.app.hazop_entries = d.entries
                break
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New HAZOP", "Name:")
        if not name:
            return
        doc = HazopDoc(name, [])
        self.app.hazop_docs.append(doc)
        self.app.active_hazop = doc
        self.app.hazop_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.hazop_entries:
            vals = [
                row.function,
                row.malfunction,
                row.mtype,
                row.scenario,
                row.conditions,
                row.hazard,
                "Yes" if row.safety else "No",
                row.rationale,
                "Yes" if row.covered else "No",
                row.covered_by,
            ]
            self.tree.insert("", "end", values=vals)
        self.update_mal_explorer()

    def update_mal_explorer(self, *_):
        sel = self.tree.focus()
        self.mal_list.delete(0, tk.END)
        if not sel:
            return
        idx = self.tree.index(sel)
        if idx >= len(self.app.hazop_entries):
            return
        row = self.app.hazop_entries[idx]
        modes = self.app.get_failure_modes_for_malfunction(row.malfunction)
        for m in modes:
            self.mal_list.insert(tk.END, m)

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, row=None):
            self.app = parent.app
            self.row = row or HazopEntry(
                "",
                "",
                "No/Not",
                "",
                "",
                "",
                False,
                "",
                False,
                "",
            )
            super().__init__(parent, title="Edit HAZOP Row")

        def body(self, master):
            ttk.Label(master, text="Function").grid(row=0, column=0, sticky="e", padx=5, pady=5)
            funcs = self.app.get_all_action_names()
            self.func = tk.StringVar(value=self.row.function)
            ttk.Combobox(master, textvariable=self.func, values=funcs, state="readonly").grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(master, text="Malfunction").grid(row=1, column=0, sticky="e", padx=5, pady=5)
            self.mal = tk.StringVar(value=self.row.malfunction)
            ttk.Entry(master, textvariable=self.mal).grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(master, text="Type").grid(row=2, column=0, sticky="e", padx=5, pady=5)
            self.typ = tk.StringVar(value=self.row.mtype)
            ttk.Combobox(
                master,
                textvariable=self.typ,
                values=["No/Not", "Unintended", "Excessive", "Insufficient", "Reverse"],
                state="readonly",
            ).grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(master, text="Scenario").grid(row=3, column=0, sticky="e", padx=5, pady=5)
            scenarios = []
            for lib in self.app.scenario_libraries:
                scenarios.extend(lib.get("scenarios", []))
            self.scen = tk.StringVar(value=self.row.scenario)
            ttk.Combobox(master, textvariable=self.scen, values=scenarios, state="readonly").grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(master, text="Driving Conditions").grid(row=4, column=0, sticky="e", padx=5, pady=5)
            self.cond = tk.StringVar(value=self.row.conditions)
            ttk.Entry(master, textvariable=self.cond).grid(row=4, column=1, padx=5, pady=5)

            ttk.Label(master, text="Hazard").grid(row=5, column=0, sticky="ne", padx=5, pady=5)
            self.haz = tk.Text(master, width=30, height=3)
            self.haz.insert("1.0", self.row.hazard)
            self.haz.grid(row=5, column=1, padx=5, pady=5)

            ttk.Label(master, text="Safety Relevant").grid(row=6, column=0, sticky="e", padx=5, pady=5)
            self.safety = tk.StringVar(value="Yes" if self.row.safety else "No")
            ttk.Combobox(master, textvariable=self.safety, values=["Yes", "No"], state="readonly").grid(row=6, column=1, padx=5, pady=5)

            ttk.Label(master, text="Rationale").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
            self.rat = tk.Text(master, width=30, height=3)
            self.rat.insert("1.0", self.row.rationale)
            self.rat.grid(row=7, column=1, padx=5, pady=5)

            ttk.Label(master, text="Covered").grid(row=8, column=0, sticky="e", padx=5, pady=5)
            self.cov = tk.StringVar(value="Yes" if self.row.covered else "No")
            ttk.Combobox(master, textvariable=self.cov, values=["Yes", "No"], state="readonly").grid(row=8, column=1, padx=5, pady=5)

            ttk.Label(master, text="Covered By").grid(row=9, column=0, sticky="e", padx=5, pady=5)
            malfs = [e.malfunction for e in self.app.hazop_entries]
            self.cov_by = tk.StringVar(value=self.row.covered_by)
            ttk.Combobox(master, textvariable=self.cov_by, values=malfs, state="readonly").grid(row=9, column=1, padx=5, pady=5)

        def apply(self):
            self.row.function = self.func.get()
            self.row.malfunction = self.mal.get()
            self.row.mtype = self.typ.get()
            self.row.scenario = self.scen.get()
            self.row.conditions = self.cond.get()
            self.row.hazard = self.haz.get("1.0", "end-1c")
            self.row.safety = self.safety.get() == "Yes"
            self.row.rationale = self.rat.get("1.0", "end-1c")
            self.row.covered = self.cov.get() == "Yes"
            self.row.covered_by = self.cov_by.get()

    def add_row(self):
        if not self.app.active_hazop:
            messagebox.showwarning("Add", "Create a HAZOP first")
            return
        dlg = self.RowDialog(self)
        if dlg.row.function:
            self.app.hazop_entries.append(dlg.row)
            self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        row = self.app.hazop_entries[idx]
        dlg = self.RowDialog(self, row)
        self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.hazop_entries):
                del self.app.hazop_entries[idx]
        self.refresh()

    def load_analysis(self):
        if not self.app.reliability_analyses:
            messagebox.showwarning("Load", "No saved analyses")
            return
        win = tk.Toplevel(self)
        win.title("Select Analysis")
        lb = tk.Listbox(win, height=8, width=40)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for ra in self.app.reliability_analyses:
            lb.insert(tk.END, ra.name)
        def do_load():
            sel = lb.curselection()
            if not sel:
                return
            ra = self.app.reliability_analyses[sel[0]]
            self.standard_var.set(ra.standard)
            self.profile_var.set(ra.profile)
            self.components = copy.deepcopy(ra.components)
            self.app.reliability_total_fit = ra.total_fit
            self.app.spfm = ra.spfm
            self.app.lpfm = ra.lpfm
            self.app.reliability_dc = ra.dc
            win.destroy()
            self.refresh_tree()
            self.formula_label.config(
                text=f"Total FIT: {ra.total_fit:.2f}  DC: {ra.dc:.2f}  SPFM: {ra.spfm:.2f}  LPFM: {ra.lpfm:.2f}"
            )
        ttk.Button(win, text="Load", command=do_load).pack(side=tk.RIGHT, padx=5, pady=5)

    def save_analysis(self):
        if not self.components:
            messagebox.showwarning("Save", "No components defined")
            return
        name = simpledialog.askstring("Save Analysis", "Enter analysis name:")
        if not name:
            return
        ra = ReliabilityAnalysis(
            name,
            self.standard_var.get(),
            self.profile_var.get(),
            copy.deepcopy(self.components),
            self.app.reliability_total_fit,
            self.app.spfm,
            self.app.lpfm,
            self.app.reliability_dc,
        )
        self.app.reliability_analyses.append(ra)
        messagebox.showinfo("Save", "Analysis saved")


class HaraWindow(tk.Frame):
    COLS = [
        "malfunction","hazard","severity","sev_rationale","controllability",
        "cont_rationale","exposure","exp_rationale","asil","safety_goal"
    ]

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("HARA Analysis")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="HARA:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)
        self.hazop_lbl = ttk.Label(top, text="")
        self.hazop_lbl.pack(side=tk.LEFT, padx=10)
        self.status_lbl = ttk.Label(top, text="")
        self.status_lbl.pack(side=tk.LEFT, padx=10)

        self.tree = ttk.Treeview(self, columns=self.COLS, show="headings")
        for c in self.COLS:
            self.tree.heading(c, text=c.replace("_"," ").title())
            width = 200 if c == "hazard" else 120
            self.tree.column(c, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text="Add", command=self.add_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Edit", command=self.edit_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Delete", command=self.del_row).pack(side=tk.LEFT, padx=2, pady=2)
        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh_docs(self):
        self.app.update_hara_statuses()
        names = [d.name for d in self.app.hara_docs]
        # Explicitly configure the combobox values to ensure Tkinter updates
        self.doc_cb.configure(values=names)
        if self.app.active_hara:
            self.doc_var.set(self.app.active_hara.name)
            hazops = ", ".join(getattr(self.app.active_hara, "hazops", []))
            self.hazop_lbl.config(text=f"HAZOPs: {hazops}")
            self.status_lbl.config(text=f"Status: {getattr(self.app.active_hara, 'status', 'draft')}")

        elif names:
            self.doc_var.set(names[0])
            doc = self.app.hara_docs[0]
            hazops = ", ".join(getattr(doc, "hazops", []))
            self.hazop_lbl.config(text=f"HAZOPs: {hazops}")
            self.app.active_hara = doc
            self.app.hara_entries = doc.entries
            self.status_lbl.config(text=f"Status: {getattr(doc, 'status', 'draft')}")

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.hara_docs:
            if d.name == name:
                self.app.active_hara = d
                self.app.hara_entries = d.entries
                hazops = ", ".join(getattr(d, "hazops", []))
                self.hazop_lbl.config(text=f"HAZOPs: {hazops}")
                self.status_lbl.config(text=f"Status: {getattr(d, 'status', 'draft')}")
                break
        self.refresh()

    class NewHaraDialog(simpledialog.Dialog):
        def __init__(self, parent, app):
            self.app = app
            super().__init__(parent, title="New HARA")

        def body(self, master):
            ttk.Label(master, text="Name").grid(row=0, column=0, sticky="e")
            self.name_var = tk.StringVar()
            ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1)
            ttk.Label(master, text="HAZOPs").grid(row=1, column=0, sticky="ne")
            names = [d.name for d in self.app.hazop_docs]
            self.hazop_lb = tk.Listbox(master, selectmode="extended", height=5)
            for n in names:
                self.hazop_lb.insert(tk.END, n)
            self.hazop_lb.grid(row=1, column=1)

        def apply(self):
            sel = [self.hazop_lb.get(i) for i in self.hazop_lb.curselection()]
            self.result = (self.name_var.get(), sel)

    def new_doc(self):
        dlg = self.NewHaraDialog(self, self.app)
        if not getattr(dlg, "result", None):
            return
        name, hazops = dlg.result
        doc = HaraDoc(name, hazops, [], False, "draft")
        self.app.hara_docs.append(doc)
        self.app.active_hara = doc
        self.app.hara_entries = doc.entries
        self.status_lbl.config(text=f"Status: {doc.status}")
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.hara_entries:
            vals = [
                row.malfunction, row.hazard,
                row.severity, row.sev_rationale,
                row.controllability, row.cont_rationale,
                row.exposure, row.exp_rationale,
                row.asil, row.safety_goal
            ]
            self.tree.insert("", "end", values=vals)
        self.app.sync_hara_to_safety_goals()

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, app, row=None):
            self.app = app
            self.row = row or HaraEntry("","",1,"",1,"",1,"","QM","")
            super().__init__(parent, title="Edit HARA Row")

        def body(self, master):
            hazop_names = []
            if self.app.active_hara:
                hazop_names = getattr(self.app.active_hara, "hazops", []) or []
            malfs = set()
            if not hazop_names:
                hazop_names = [d.name for d in self.app.hazop_docs]
            for hz_name in hazop_names:
                hz = self.app.get_hazop_by_name(hz_name)
                if hz:
                    for e in hz.entries:
                        if getattr(e, "safety", False):
                            malfs.add(e.malfunction)
            malfs = sorted(malfs)
            goals = [te.safety_goal_description or (te.user_name or f"SG {te.unique_id}") for te in self.app.top_events]
            ttk.Label(master, text="Malfunction").grid(row=0,column=0,sticky="e")
            self.mal_var = tk.StringVar(value=self.row.malfunction)
            ttk.Combobox(master, textvariable=self.mal_var, values=malfs, state="readonly").grid(row=0,column=1)
            ttk.Label(master, text="Hazard").grid(row=1,column=0,sticky="ne")
            self.haz = tk.Text(master, width=30, height=3)
            self.haz.insert("1.0", self.row.hazard)
            self.haz.grid(row=1,column=1)
            ttk.Label(master, text="Severity").grid(row=2,column=0,sticky="e")
            self.sev_var = tk.StringVar(value=str(self.row.severity))
            sev_cb = ttk.Combobox(master, textvariable=self.sev_var, values=["1","2","3"], state="readonly")
            sev_cb.grid(row=2,column=1)
            ttk.Label(master, text="Severity Rationale").grid(row=3,column=0,sticky="e")
            self.sev_rat = tk.Entry(master)
            self.sev_rat.insert(0, self.row.sev_rationale)
            self.sev_rat.grid(row=3,column=1)
            ttk.Label(master, text="Controllability").grid(row=4,column=0,sticky="e")
            self.cont_var = tk.StringVar(value=str(self.row.controllability))
            cont_cb = ttk.Combobox(master, textvariable=self.cont_var, values=["1","2","3"], state="readonly")
            cont_cb.grid(row=4,column=1)
            ttk.Label(master, text="Controllability Rationale").grid(row=5,column=0,sticky="e")
            self.cont_rat = tk.Entry(master)
            self.cont_rat.insert(0, self.row.cont_rationale)
            self.cont_rat.grid(row=5,column=1)
            ttk.Label(master, text="Exposure").grid(row=6,column=0,sticky="e")
            self.exp_var = tk.StringVar(value=str(self.row.exposure))
            exp_cb = ttk.Combobox(master, textvariable=self.exp_var, values=["1","2","3","4"], state="readonly")
            exp_cb.grid(row=6,column=1)
            ttk.Label(master, text="Exposure Rationale").grid(row=7,column=0,sticky="e")
            self.exp_rat = tk.Entry(master)
            self.exp_rat.insert(0, self.row.exp_rationale)
            self.exp_rat.grid(row=7,column=1)
            ttk.Label(master, text="ASIL").grid(row=8,column=0,sticky="e")
            self.asil_var = tk.StringVar(value=self.row.asil)
            asil_lbl = ttk.Label(master, textvariable=self.asil_var)
            asil_lbl.grid(row=8,column=1)
            ttk.Label(master, text="Safety Goal").grid(row=9,column=0,sticky="e")
            self.sg_var = tk.StringVar(value=self.row.safety_goal)
            ttk.Combobox(master, textvariable=self.sg_var, values=goals, state="readonly").grid(row=9,column=1)

            def recalc(_=None):
                try:
                    s = int(self.sev_var.get())
                    c = int(self.cont_var.get())
                    e = int(self.exp_var.get())
                except ValueError:
                    self.asil_var.set("QM")
                    return
                self.asil_var.set(calc_asil(s,c,e))

            sev_cb.bind("<<ComboboxSelected>>", recalc)
            cont_cb.bind("<<ComboboxSelected>>", recalc)
            exp_cb.bind("<<ComboboxSelected>>", recalc)
            recalc()

        def apply(self):
            self.row.malfunction = self.mal_var.get()
            self.row.hazard = self.haz.get("1.0", "end-1c")
            self.row.severity = int(self.sev_var.get())
            self.row.sev_rationale = self.sev_rat.get()
            self.row.controllability = int(self.cont_var.get())
            self.row.cont_rationale = self.cont_rat.get()
            self.row.exposure = int(self.exp_var.get())
            self.row.exp_rationale = self.exp_rat.get()
            self.row.asil = self.asil_var.get()
            self.row.safety_goal = self.sg_var.get()

    def add_row(self):
        if not self.app.active_hara:
            messagebox.showwarning("Add", "Create a HARA first")
            return
        dlg = self.RowDialog(self, self.app)
        self.app.hara_entries.append(dlg.row)
        if self.app.active_hara:
            self.app.active_hara.status = "draft"
            self.app.active_hara.approved = False
            self.app.invalidate_reviews_for_hara(self.app.active_hara.name)
            self.status_lbl.config(text=f"Status: {self.app.active_hara.status}")
        self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        dlg = self.RowDialog(self, self.app, self.app.hara_entries[idx])
        if self.app.active_hara:
            self.app.active_hara.status = "draft"
            self.app.active_hara.approved = False
            self.app.invalidate_reviews_for_hara(self.app.active_hara.name)
            self.status_lbl.config(text=f"Status: {self.app.active_hara.status}")
        self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.hara_entries):
                del self.app.hara_entries[idx]
        if self.app.active_hara:
            self.app.active_hara.status = "draft"
            self.app.active_hara.approved = False
            self.app.invalidate_reviews_for_hara(self.app.active_hara.name)
            self.status_lbl.config(text=f"Status: {self.app.active_hara.status}")
        self.refresh()

    def approve_doc(self):
        if not self.app.active_hara:
            return
        self.app.active_hara.status = "closed"
        self.app.active_hara.approved = True
        self.app.update_hara_statuses()
        self.app.ensure_asil_consistency()
        self.app.update_views()
        messagebox.showinfo("HARA", "HARA approved")


class TC2FIWindow(tk.Frame):
    COLS = [
        "id",
        "known_use_case",
        "occurrence",
        "impacted_function",
        "arch_elements",
        "interfaces",
        "functional_insufficiency",
        "vehicle_effect",
        "severity",
        "design_measures",
        "verification",
        "measure_effectiveness",
        "scene",
        "scenario",
        "driver_behavior",
        "triggering_condition",
        "tc_effect",
        "mitigation",
        "acceptance",
    ]

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("TC2FI Analysis")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="TC2FI:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        if isinstance(master, tk.Toplevel):
            master.geometry("800x400")
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        style = ttk.Style(self)
        style.configure("TC2FI.Treeview", rowheight=80)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.COLS,
            show="headings",
            style="TC2FI.Treeview",
            height=4,
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in self.COLS:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=120)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self.edit_row())
        btn = ttk.Frame(self)
        btn.pack()
        ttk.Button(btn, text="Add", command=self.add_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Edit", command=self.edit_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Delete", command=self.del_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2, pady=2)
        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.tc2fi_entries:
            vals = [_wrap_val(row.get(k, "")) for k in self.COLS]
            self.tree.insert("", "end", values=vals)

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, app, data=None):
            self.app = app
            default = {k: "" for k in TC2FIWindow.COLS}
            self.data = data or default
            super().__init__(parent, title="Edit Row")

        def body(self, master):
            tc_names = [n.user_name or f"TC {n.unique_id}" for n in self.app.get_all_triggering_conditions()]
            fi_names = [n.user_name or f"FI {n.unique_id}" for n in self.app.get_all_functional_insufficiencies()]
            func_names = self.app.get_all_function_names()
            comp_names = self.app.get_all_component_names()
            scen_names = self.app.get_all_scenario_names()
            scene_names = self.app.get_all_scenery_names()
            self.widgets = {}
            r = 0

            def refresh_funcs(*_):
                comp = self.widgets.get("arch_elements")
                if isinstance(comp, tk.StringVar):
                    opts = sorted({e.function for e in self.app.hazop_entries if not comp.get() or e.component == comp.get()})
                else:
                    opts = func_names
                if "impacted_function" in self.widgets:
                    w = self.widgets["impacted_function_widget"]
                    w["values"] = opts

            for col in TC2FIWindow.COLS:
                ttk.Label(master, text=col.replace("_", " ").title()).grid(row=r, column=0, sticky="e", padx=5, pady=2)
                if col == "functional_insufficiency":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=fi_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "triggering_condition":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=tc_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "impacted_function":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=func_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                    self.widgets["impacted_function_widget"] = cb
                elif col == "arch_elements":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=comp_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    cb.bind("<<ComboboxSelected>>", refresh_funcs)
                    self.widgets[col] = var
                elif col == "scene":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=scene_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "scenario":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=scen_names, state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "severity":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(master, textvariable=var, values=["1", "2", "3"], state="readonly")
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                else:
                    txt = tk.Text(master, width=25, height=2, wrap="word")
                    txt.insert("1.0", self.data.get(col, ""))
                    txt.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = txt
                r += 1
            refresh_funcs()

        def apply(self):
            for col, widget in self.widgets.items():
                if isinstance(widget, tk.Entry):
                    self.data[col] = widget.get()
                elif isinstance(widget, tk.Text):
                    self.data[col] = widget.get("1.0", "end-1c")
                else:
                    self.data[col] = widget.get()

            self.result = True
    def add_row(self):
        dlg = self.RowDialog(self, self.app)
        if getattr(dlg, "result", None):
            self.app.tc2fi_entries.append(dlg.data)
            self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        data = self.app.tc2fi_entries[idx]
        dlg = self.RowDialog(self, self.app, data)
        if getattr(dlg, "result", None):
            self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.tc2fi_entries):
                del self.app.tc2fi_entries[idx]
        self.refresh()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(self.COLS)
            for r in self.app.tc2fi_entries:
                w.writerow([r.get(k, "") for k in self.COLS])
        messagebox.showinfo("Export", "TC2FI exported")

    def refresh_docs(self):
        names = [d.name for d in self.app.tc2fi_docs]
        self.doc_cb.configure(values=names)
        if self.app.active_tc2fi:
            self.doc_var.set(self.app.active_tc2fi.name)
        elif names:
            self.doc_var.set(names[0])

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.tc2fi_docs:
            if d.name == name:
                self.app.active_tc2fi = d
                self.app.tc2fi_entries = d.entries
                break
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New TC2FI", "Name:")
        if not name:
            return
        doc = TC2FIDoc(name, [])
        self.app.tc2fi_docs.append(doc)
        self.app.active_tc2fi = doc
        self.app.tc2fi_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_tc2fi:
            return
        name = simpledialog.askstring(
            "Rename TC2FI", "Name:", initialvalue=self.app.active_tc2fi.name
        )
        if not name:
            return
        self.app.active_tc2fi.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_tc2fi
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete TC2FI '{doc.name}'?"):
            return
        self.app.tc2fi_docs.remove(doc)
        if self.app.tc2fi_docs:
            self.app.active_tc2fi = self.app.tc2fi_docs[0]
        else:
            self.app.active_tc2fi = None
        self.app.tc2fi_entries = (
            self.app.active_tc2fi.entries if self.app.active_tc2fi else []
        )
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

class HazardExplorerWindow(tk.Toplevel):
    """Read-only list of hazards per HARA."""

    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("Hazard Explorer")

        columns = ("HARA", "Malfunction", "Hazard")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for c in columns:
            self.tree.heading(c, text=c)
            width = 200 if c == "Hazard" else 120
            self.tree.column(c, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self, text="Export CSV", command=self.export_csv).pack(pady=5)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for doc in self.app.hara_docs:
            for e in doc.entries:
                self.tree.insert(
                    "",
                    "end",
                    values=(doc.name, e.malfunction, getattr(e, "hazard", "")),
                )

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["HARA", "Malfunction", "Hazard"])
            for iid in self.tree.get_children():
                w.writerow(self.tree.item(iid, "values"))
        messagebox.showinfo("Export", "Hazards exported")
