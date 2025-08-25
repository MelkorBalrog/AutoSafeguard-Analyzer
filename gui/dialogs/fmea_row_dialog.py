"""Dialog for editing FMEA entries."""
from __future__ import annotations

import datetime
import types
import uuid
import tkinter as tk
from tkinter import ttk, simpledialog

from gui.controls import messagebox
from gui.dialogs.edit_node_dialog import EditNodeDialog, format_requirement
from analysis.models import global_requirements, ensure_requirement_defaults
from analysis.user_config import CURRENT_USER_NAME
from analysis.fmeda_utils import GATE_NODE_TYPES

class FMEARowDialog(simpledialog.Dialog):
    def __init__(self, parent, node, app, fmea_entries, mechanisms=None, hide_diagnostics=False, is_fmeda=False):
        self.node = node
        self.app = app
        self.fmea_entries = fmea_entries
        self.mechanisms = mechanisms or []
        self.hide_diagnostics = hide_diagnostics
        self.is_fmeda = is_fmeda
        super().__init__(parent, title="Edit FMEA Entry")
        self.app.selected_node = node

    def body(self, master):
        self.resizable(False, False)
        nb = ttk.Notebook(master)
        nb.pack(fill=tk.BOTH, expand=True)
        gen_frame = ttk.Frame(nb)
        metric_frame = ttk.Frame(nb)
        nb.add(gen_frame, text="General")
        nb.add(metric_frame, text="Metrics")

        ttk.Label(gen_frame, text="Component:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        if self.node.parents and getattr(self.node.parents[0], "node_type", "").upper() not in GATE_NODE_TYPES:
            comp = self.node.parents[0].user_name or f"Node {self.node.parents[0].unique_id}"
        else:
            comp = getattr(self.node, "fmea_component", "")
        comp_names = {c.name for c in self.app.reliability_components}
        part_names = set(self.app.get_all_part_names())
        comp_names.update(part_names)
        # Gather failure modes from gates and FMEA/FMEDA tables only
        basic_events = self.app.get_non_basic_failure_modes()
        for be in basic_events:
            src = self.app.get_failure_mode_node(be)
            parent = src.parents[0] if src.parents else None
            if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES and parent.user_name:
                comp_names.add(parent.user_name)
            else:
                name = getattr(src, "fmea_component", "")
                if name:
                    comp_names.add(name)
        self.comp_var = tk.StringVar(value=comp)
        self.comp_combo = ttk.Combobox(
            gen_frame, textvariable=self.comp_var,
            values=sorted(comp_names), width=30
        )
        self.comp_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(gen_frame, text="Failure Mode:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        # Include failure modes from both the FTA and any FMEA specific
        # entries so the combo box always lists all available modes.
        self.mode_map = {
            be.description: be
            for be in basic_events
            if getattr(be, "description", "").strip()
        }
        for doc in self.app.hazop_docs:
            for e in doc.entries:
                label = f"{e.function}: {e.malfunction}"
                obj = types.SimpleNamespace(
                    description=e.malfunction,
                    user_name=label,
                    parents=[],
                    fmea_component=e.component,
                )
                self.mode_map[label] = obj
        mode_names = list(self.mode_map.keys())
        self.mode_var = tk.StringVar(value=self.node.description or self.node.user_name)
        self.mode_combo = ttk.Combobox(gen_frame, textvariable=self.mode_var,
                                      values=mode_names, width=30)
        self.mode_combo.grid(row=1, column=1, padx=5, pady=5)

        def auto_fault():
            comp = self.comp_var.get().strip()
            mode = self.mode_var.get().strip()
            if not comp or not mode:
                return
            if comp not in part_names:
                name = f"{comp} is {mode}"
                if name not in self.fault_names:
                    self.cause_list.insert(tk.END, name)
                    self.fault_names.append(name)
                idx = self.fault_names.index(name)
                self.cause_list.selection_clear(0, tk.END)
                self.cause_list.select_set(idx)

        def mode_sel(_):
            label = self.mode_var.get()
            src = self.mode_map.get(label)
            if src:
                comp_name = self.app.get_component_name_for_node(src)
                if comp_name:
                    self.comp_var.set(comp_name)
                    comp_sel()
                faults = self.app.get_faults_for_failure_mode(src)
                if faults:
                    self.cause_list.selection_clear(0, tk.END)
                    for i, name in enumerate(fault_names):
                        if name in faults:
                            self.cause_list.select_set(i)
                else:
                    auto_fault()
        
        self.mode_combo.bind("<<ComboboxSelected>>", mode_sel)

        self.effect_text = tk.Text(gen_frame, width=30, height=3)
        self.effect_text.insert("1.0", self.node.fmea_effect)
        row_next = 2
        if not self.is_fmeda:
            ttk.Label(gen_frame, text="Failure Effect:").grid(row=row_next, column=0, sticky="e", padx=5, pady=5)
            self.effect_text.grid(row=row_next, column=1, padx=5, pady=5)
            row_next += 1

        ttk.Label(gen_frame, text="Related Fault:").grid(row=row_next, column=0, sticky="ne", padx=5, pady=5)
        fault_names = list(sorted(set(self.app.faults)))
        self.fault_names = fault_names
        self.cause_list = tk.Listbox(gen_frame, selectmode=tk.MULTIPLE, height=4, exportselection=False)
        for name in fault_names:
            self.cause_list.insert(tk.END, name)
        current_causes = [c.strip() for c in getattr(self.node, 'fmea_cause', '').split(';') if c.strip()]
        for i, name in enumerate(fault_names):
            if name in current_causes:
                self.cause_list.select_set(i)
        self.cause_list.grid(row=row_next, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(gen_frame, text="Add Fault", command=self.add_fault).grid(row=row_next, column=2, padx=5, pady=5)
        row_next += 1

        ttk.Label(gen_frame, text="Malfunction Effect:").grid(row=row_next, column=0, sticky="ne", padx=5, pady=5)
        sel_mals = [m.strip() for m in getattr(self.node, 'fmeda_malfunction', '').split(';') if m.strip()]
        self.mal_sel_var = tk.StringVar(value=";".join(sel_mals))
        def update_sg(*_):
            if self.is_fmeda:
                selected = [m for m, v in self.mal_vars.items() if v.get()]
            else:
                selected = [self.mal_var.get()] if self.mal_var.get() else []
            goals = self.app.get_safety_goals_for_malfunctions(selected)
            if not goals:
                goals = self.app.get_top_event_safety_goals(self.node)
            self.sg_var.set(", ".join(goals))
            if self.is_fmeda:
                sel = [m for m, v in self.mal_vars.items() if v.get()]
                if sel:
                    self.mal_sel_var.set(";".join(sel))
            else:
                if self.mal_var.get():
                    self.mal_sel_var.set(self.mal_var.get())

        if self.is_fmeda:
            self.mal_vars = {}
            self.mal_frame = ttk.Frame(gen_frame)
            self.mal_frame.grid(row=row_next, column=1, padx=5, pady=5, sticky="w")
            for m in sorted(self.app.malfunctions):
                var = tk.BooleanVar(value=False)
                ttk.Checkbutton(self.mal_frame, text=m, variable=var, command=update_sg).pack(anchor="w")
                self.mal_vars[m] = var
        else:
            self.mal_var = tk.StringVar(value="")
            self.mal_combo = ttk.Combobox(
                gen_frame,
                textvariable=self.mal_var,
                values=sorted(self.app.malfunctions),
                state="readonly",
                width=30,
            )
            self.mal_combo.grid(row=row_next, column=1, padx=5, pady=5, sticky="w")
            self.mal_combo.bind("<<ComboboxSelected>>", update_sg)

        row_next += 1
        ttk.Label(gen_frame, textvariable=self.mal_sel_var, foreground="blue").grid(row=row_next, column=1, padx=5, pady=5, sticky="w")
        row_next += 1

        ttk.Label(gen_frame, text="Violates Safety Goal:").grid(row=row_next, column=0, sticky="e", padx=5, pady=5)
        preset_goals = self.app.get_safety_goals_for_malfunctions(sel_mals) or \
            self.app.get_top_event_safety_goals(self.node)
        sg_value = ", ".join(preset_goals) if preset_goals else getattr(self.node, 'fmeda_safety_goal', '')
        self.sg_var = tk.StringVar(value=sg_value)
        self.sg_entry = ttk.Entry(gen_frame, textvariable=self.sg_var, width=30, state='readonly')
        self.sg_entry.grid(row=row_next, column=1, padx=5, pady=5)

        ttk.Label(metric_frame, text="Severity (1-10):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.sev_spin = tk.Spinbox(metric_frame, from_=1, to=10, width=5)
        self.sev_spin.delete(0, tk.END)
        self.sev_spin.insert(0, str(self.node.fmea_severity))
        self.sev_spin.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(metric_frame, text="Occurrence (1-10):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.occ_spin = tk.Spinbox(metric_frame, from_=1, to=10, width=5)
        self.occ_spin.delete(0, tk.END)
        self.occ_spin.insert(0, str(self.node.fmea_occurrence))
        self.occ_spin.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(metric_frame, text="Detection (1-10):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.det_spin = tk.Spinbox(metric_frame, from_=1, to=10, width=5)
        self.det_spin.delete(0, tk.END)
        self.det_spin.insert(0, str(self.node.fmea_detection))
        self.det_spin.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        row = 3
        if not self.hide_diagnostics:
            ttk.Label(metric_frame, text="Diag Coverage (0-1):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.dc_var = tk.DoubleVar(value=getattr(self.node, 'fmeda_diag_cov', 0.0))
            ttk.Entry(metric_frame, textvariable=self.dc_var, width=5).grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1

            ttk.Label(metric_frame, text="Mechanism:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.mech_var = tk.StringVar(value=getattr(self.node, 'fmeda_mechanism', ''))
            self.mech_combo = ttk.Combobox(metric_frame, textvariable=self.mech_var, values=[m.name for m in self.mechanisms], state='readonly', width=30)
            self.mech_combo.grid(row=row, column=1, padx=5, pady=5)

            def mech_sel(_):
                name = self.mech_var.get()
                for m in self.mechanisms:
                    if m.name == name:
                        self.dc_var.set(m.coverage)
                        req_text = getattr(m, "requirement", "")
                        if req_text:
                            global global_requirements
                            req = next(
                                (
                                    r
                                    for r in global_requirements.values()
                                    if r.get("text") == req_text
                                ),
                                None,
                            )
                            if req is None:
                                rid = str(uuid.uuid4())
                                req = {
                                    "id": rid,
                                    "req_type": REQUIREMENT_TYPE_OPTIONS[0],
                                    "text": req_text,
                                    "asil": "",
                                }
                                ensure_requirement_defaults(req)
                                global_requirements[rid] = req
                            if not hasattr(self.node, "safety_requirements"):
                                self.node.safety_requirements = []
                            if not any(r.get("id") == req["id"] for r in self.node.safety_requirements):
                                self.node.safety_requirements.append(req)
                                desc = format_requirement(req, include_id=False)
                                self.req_listbox.insert(tk.END, desc)
                        break

            self.mech_combo.bind("<<ComboboxSelected>>", mech_sel)
            mech_sel(None)
            row += 1
        else:
            self.dc_var = tk.DoubleVar(value=0.0)
            self.mech_var = tk.StringVar(value="")

        ttk.Label(metric_frame, text="Fault Type:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.ftype_var = tk.StringVar(value=getattr(self.node, 'fmeda_fault_type', 'permanent'))
        ttk.Combobox(metric_frame, textvariable=self.ftype_var, values=['permanent', 'transient'], state='readonly', width=10).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        ttk.Label(metric_frame, text="Fault Fraction:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.ffrac_var = tk.DoubleVar(value=getattr(self.node, 'fmeda_fault_fraction', 1.0))
        ttk.Entry(metric_frame, textvariable=self.ffrac_var, width=5).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        ttk.Label(metric_frame, text="FIT Rate:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.fit_var = tk.DoubleVar(value=getattr(self.node, 'fmeda_fit', 0.0))
        ttk.Entry(metric_frame, textvariable=self.fit_var, width=10).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        def comp_sel(_=None):
            name = self.comp_var.get()
            comp = next((c for c in self.app.reliability_components if c.name == name), None)
            if comp is not None:
                self.fit_var.set(comp.fit)
            auto_fault()

        self.comp_combo.bind("<<ComboboxSelected>>", comp_sel)
        comp_sel()
        mode_sel(None)
        auto_fault()

        row += 1
        ttk.Label(metric_frame, text="DC Target:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        fta_goal = next((g for g in self.app.top_events if g.user_name == self.sg_var.get()), None)
        val = getattr(fta_goal, "sg_dc_target", 0.0) if fta_goal else getattr(self.node, 'fmeda_dc_target', 0.0)
        state = 'disabled' if fta_goal else 'normal'
        self.dc_target_var = tk.DoubleVar(value=val)
        tk.Entry(metric_frame, textvariable=self.dc_target_var, width=8, state=state).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        ttk.Label(metric_frame, text="SPFM Target:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        val = getattr(fta_goal, "sg_spfm_target", 0.0) if fta_goal else getattr(self.node, 'fmeda_spfm_target', 0.0)
        state = 'disabled' if fta_goal else 'normal'
        self.spfm_target_var = tk.DoubleVar(value=val)
        tk.Entry(metric_frame, textvariable=self.spfm_target_var, width=8, state=state).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        ttk.Label(metric_frame, text="LPFM Target:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        val = getattr(fta_goal, "sg_lpfm_target", 0.0) if fta_goal else getattr(self.node, 'fmeda_lpfm_target', 0.0)
        state = 'disabled' if fta_goal else 'normal'
        self.lpfm_target_var = tk.DoubleVar(value=val)
        tk.Entry(metric_frame, textvariable=self.lpfm_target_var, width=8, state=state).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        ttk.Label(metric_frame, text="Requirements:").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        self.req_frame = ttk.Frame(metric_frame)
        self.req_frame.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.req_listbox = tk.Listbox(self.req_frame, height=4, width=40)
        self.req_listbox.grid(row=0, column=0, columnspan=3, sticky="w")
        if not hasattr(self.node, "safety_requirements"):
            self.node.safety_requirements = []
        for req in self.node.safety_requirements:
            desc = format_requirement(req, include_id=False)
            self.req_listbox.insert(tk.END, desc)
        ttk.Button(self.req_frame, text="Add New", command=self.add_safety_requirement).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(self.req_frame, text="Edit", command=self.edit_safety_requirement).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(self.req_frame, text="Delete", command=self.delete_safety_requirement).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(self.req_frame, text="Add Existing", command=self.add_existing_requirement).grid(row=1, column=3, padx=2, pady=2)
        ttk.Button(self.req_frame, text="Comment", command=self.comment_requirement).grid(row=1, column=4, padx=2, pady=2)
        ttk.Button(self.req_frame, text="Comment FMEA", command=self.comment_fmea).grid(row=1, column=5, padx=2, pady=2)
        return self.effect_text

    def apply(self):
        comp = self.comp_var.get()
        if self.node.parents and getattr(self.node.parents[0], "node_type", "").upper() not in GATE_NODE_TYPES:
            self.node.parents[0].user_name = comp
        # Always store the component name so it can be restored on load
        self.node.fmea_component = comp
        self.node.description = self.mode_var.get()
        new_effect = self.effect_text.get("1.0", "end-1c")
        if self.node.fmea_effect and self.node.fmea_effect != new_effect:
            self.app.rename_failure(self.node.fmea_effect, new_effect)
        self.node.fmea_effect = new_effect
        sel = [self.cause_list.get(i) for i in self.cause_list.curselection()]
        old_causes = [c.strip() for c in getattr(self.node, "fmea_cause", "").split(";") if c.strip()]
        self.node.fmea_cause = ";".join(sel)
        if len(old_causes) == len(sel):
            for o, n in zip(old_causes, sel):
                if o != n:
                    self.app.rename_fault(o, n)
        for name in sel:
            if name and name not in self.app.faults:
                self.app.faults.append(name)
        try:
            self.node.fmea_severity = int(self.sev_spin.get())
        except ValueError:
            self.node.fmea_severity = 1
        try:
            self.node.fmea_occurrence = int(self.occ_spin.get())
        except ValueError:
            self.node.fmea_occurrence = 1
        try:
            self.node.fmea_detection = int(self.det_spin.get())
        except ValueError:
            self.node.fmea_detection = 1
        old_mal = self.node.fmeda_malfunction
        if self.is_fmeda:
            selected_mals = [m for m, v in self.mal_vars.items() if v.get()]
            if not selected_mals:
                selected_mals = [m.strip() for m in self.mal_sel_var.get().split(';') if m.strip()]
            mal_value = ";".join(selected_mals)
        else:
            mal_value = self.mal_var.get().strip() or self.mal_sel_var.get().strip()
            selected_mals = [mal_value] if mal_value else []
        if old_mal and old_mal != mal_value:
            self.app.rename_malfunction(old_mal, mal_value)
        self.node.fmeda_malfunction = mal_value
        self.node.fmeda_safety_goal = self.sg_var.get()
        try:
            self.node.fmeda_diag_cov = float(self.dc_var.get())
        except ValueError:
            self.node.fmeda_diag_cov = 0.0
        self.node.fmeda_mechanism = self.mech_var.get()
        if self.hide_diagnostics:
            self.node.fmeda_diag_cov = 0.0
            self.node.fmeda_mechanism = ""
        self.node.fmeda_fault_type = self.ftype_var.get()
        try:
            self.node.fmeda_fault_fraction = float(self.ffrac_var.get())
        except ValueError:
            self.node.fmeda_fault_fraction = 0.0
        try:
            self.node.fmeda_fit = float(self.fit_var.get())
        except ValueError:
            self.node.fmeda_fit = 0.0
        fta_goal = next((g for g in self.app.top_events if g.user_name == self.sg_var.get()), None)
        if not fta_goal:
            try:
                self.node.fmeda_dc_target = float(self.dc_target_var.get())
            except Exception:
                self.node.fmeda_dc_target = 0.0
            try:
                self.node.fmeda_spfm_target = float(self.spfm_target_var.get())
            except Exception:
                self.node.fmeda_spfm_target = 0.0
            try:
                self.node.fmeda_lpfm_target = float(self.lpfm_target_var.get())
            except Exception:
                self.node.fmeda_lpfm_target = 0.0
        else:
            self.node.fmeda_dc_target = getattr(fta_goal, "sg_dc_target", 0.0)
            self.node.fmeda_spfm_target = getattr(fta_goal, "sg_spfm_target", 0.0)
            self.node.fmeda_lpfm_target = getattr(fta_goal, "sg_lpfm_target", 0.0)
        self.app.propagate_failure_mode_attributes(self.node)
        self.node.modified = datetime.datetime.now().isoformat()
        self.node.modified_by = CURRENT_USER_NAME

    def add_existing_requirement(self):
        global global_requirements
        if not global_requirements:
            messagebox.showinfo("No Existing Requirements", "There are no existing requirements to add.")
            return
        dialog = EditNodeDialog.SelectExistingRequirementsDialog(self, title="Select Existing Requirements")
        if dialog.result:
            if not hasattr(self.node, "safety_requirements"):
                self.node.safety_requirements = []
            for req_id in dialog.result:
                req = global_requirements.get(req_id)
                if req and not any(r["id"] == req_id for r in self.node.safety_requirements):
                    self.node.safety_requirements.append(req)
                    desc = format_requirement(req, include_id=False)
                    self.req_listbox.insert(tk.END, desc)
        else:
            messagebox.showinfo("No Selection", "No existing requirements were selected.")

    def comment_requirement(self):
        sel = self.req_listbox.curselection()
        if not sel:
            messagebox.showwarning("Comment", "Select a requirement")
            return
        req = self.node.safety_requirements[sel[0]]
        self.app.selected_node = self.node
        # include the node id as well so the toolbox has full context
        self.app.comment_target = ("requirement", self.node.unique_id, req.get("id"))
        self.app.open_review_toolbox()

    def comment_fmea(self):
        self.app.selected_node = self.node
        self.app.comment_target = ("fmea", self.node.unique_id)
        self.app.open_review_toolbox()

    def add_fault(self):
        name = simpledialog.askstring("Add Fault", "Name:")
        if name:
            name = name.strip()
            if not name:
                return
            if name not in self.app.faults:
                self.app.add_fault(name)
                self.cause_list.insert(tk.END, name)
            for i, val in enumerate(self.cause_list.get(0, tk.END)):
                if val == name:
                    self.cause_list.selection_set(i)
                    break


    def add_safety_requirement(self):
        global global_requirements
        dialog = EditNodeDialog.RequirementDialog(self, title="Add Safety Requirement")
        if dialog.result is None or dialog.result["text"] == "":
            return
        custom_id = dialog.result.get("custom_id", "").strip()
        if not custom_id:
            custom_id = str(uuid.uuid4())
        if custom_id in global_requirements:
            req = global_requirements[custom_id]
            ensure_requirement_defaults(req)
            req["req_type"] = dialog.result["req_type"]
            req["text"] = dialog.result["text"]
            req["asil"] = dialog.result.get("asil", "QM")
        else:
            req = {
                "id": custom_id,
                "req_type": dialog.result["req_type"],
                "text": dialog.result["text"],
                "custom_id": custom_id,
                "asil": dialog.result.get("asil", "QM"),
                "validation_criteria": 0.0
            }
            ensure_requirement_defaults(req)
            global_requirements[custom_id] = req
        self.app.validation_consistency.update_validation_criteria(custom_id)
        if not hasattr(self.node, "safety_requirements"):
            self.node.safety_requirements = []
        if not any(r["id"] == custom_id for r in self.node.safety_requirements):
            self.node.safety_requirements.append(req)
            desc = format_requirement(req, include_id=False)
            self.req_listbox.insert(tk.END, desc)

    def edit_safety_requirement(self):
        selected = self.req_listbox.curselection()
        if not selected:
            messagebox.showwarning("Edit Requirement", "Select a requirement to edit.")
            return
        index = selected[0]
        current_req = self.node.safety_requirements[index]
        initial_req = current_req.copy()
        dialog = EditNodeDialog.RequirementDialog(self, title="Edit Safety Requirement", initial_req=initial_req)
        if dialog.result is None or dialog.result["text"] == "":
            return
        new_custom_id = dialog.result["custom_id"].strip() or current_req.get("custom_id") or current_req.get("id") or str(uuid.uuid4())
        current_req["req_type"] = dialog.result["req_type"]
        current_req["text"] = dialog.result["text"]
        current_req["asil"] = dialog.result.get("asil", "QM")
        current_req["custom_id"] = new_custom_id
        current_req["id"] = new_custom_id
        global_requirements[new_custom_id] = current_req
        self.app.validation_consistency.update_validation_criteria(new_custom_id)
        self.node.safety_requirements[index] = current_req
        self.req_listbox.delete(index)
        desc = format_requirement(current_req, include_id=False)
        self.req_listbox.insert(index, desc)

    def delete_safety_requirement(self):
        selected = self.req_listbox.curselection()
        if not selected:
            messagebox.showwarning("Delete Requirement", "Select a requirement to delete.")
            return
        index = selected[0]
        del self.node.safety_requirements[index]
        self.req_listbox.delete(index)

