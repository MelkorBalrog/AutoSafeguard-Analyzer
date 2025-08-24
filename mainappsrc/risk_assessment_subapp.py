from __future__ import annotations

"""Risk assessment utilities separated from the main application."""

import tkinter as tk
from tkinter import ttk, simpledialog

from gui import messagebox
from gui.toolboxes import (
    HazopWindow,
    RiskAssessmentWindow,
    FI2TCWindow,
    TC2FIWindow,
    HazardExplorerWindow,
)
from gui.stpa_window import StpaWindow
from gui.threat_window import ThreatWindow

from analysis.models import ASIL_ORDER, ASIL_TARGETS, component_fit_map


class RiskAssessmentSubApp:
    """Provide FMEDA calculations and risk propagation helpers."""

    def calculate_fmeda_metrics(self, app, events):
        total = 0.0
        unc_spf = 0.0
        unc_lpf = 0.0
        asil = "QM"
        for be in events:
            src = app.get_failure_mode_node(be)
            fit_mode = getattr(be, "fmeda_fit", 0.0)
            total += fit_mode
            if src.fmeda_fault_type == "permanent":
                unc_spf += fit_mode * (1 - src.fmeda_diag_cov)
            else:
                unc_lpf += fit_mode * (1 - src.fmeda_diag_cov)
            sg = getattr(src, "fmeda_safety_goal", "")
            sgs = app.get_top_event_safety_goals(src)
            if sgs:
                sg = ", ".join(sgs)
            a = app.get_safety_goal_asil(sg)
            if ASIL_ORDER.get(a, 0) > ASIL_ORDER.get(asil, 0):
                asil = a
        dc = (total - (unc_spf + unc_lpf)) / total if total else 0.0
        app.reliability_total_fit = total
        app.reliability_dc = dc
        app.spfm = unc_spf
        app.lpfm = unc_lpf
        spfm_metric = 1 - unc_spf / total if total else 0.0
        lpfm_metric = 1 - unc_lpf / total if total else 0.0
        return asil, dc, spfm_metric, lpfm_metric

    def compute_fmeda_metrics(self, app, events):
        comp_fit = component_fit_map(app.reliability_components)
        goal_metrics = {}
        total = spf_total = lpf_total = 0.0
        asil = "QM"
        for be in events:
            src = app.get_failure_mode_node(be)
            goals = app.get_top_event_safety_goals(src) or [getattr(src, "fmeda_safety_goal", "")]
            comp_name = app.get_component_name_for_node(src)
            fit = comp_fit.get(comp_name)
            frac = getattr(src, "fmeda_fault_fraction", 0.0)
            if frac > 1.0:
                frac /= 100.0
            value = fit * frac if fit is not None else getattr(src, "fmeda_fit", 0.0)
            fault_spf = value * (1 - src.fmeda_diag_cov) if src.fmeda_fault_type == "permanent" else 0.0
            fault_lpf = value * (1 - src.fmeda_diag_cov) if src.fmeda_fault_type != "permanent" else 0.0
            for sg in goals:
                gm = goal_metrics.setdefault(
                    sg,
                    {"total": 0.0, "spfm_raw": 0.0, "lpfm_raw": 0.0, "asil": app.get_safety_goal_asil(sg)},
                )
                gm["total"] += value
                gm["spfm_raw"] += fault_spf
                gm["lpfm_raw"] += fault_lpf
            total += value
            spf_total += fault_spf
            lpf_total += fault_lpf
            for sg in goals:
                a = app.get_safety_goal_asil(sg)
                if ASIL_ORDER.get(a, 0) > ASIL_ORDER.get(asil, 0):
                    asil = a
        for sg, vals in goal_metrics.items():
            t = vals["total"]
            spf = vals["spfm_raw"]
            lpf = vals["lpfm_raw"]
            dc = (t - (spf + lpf)) / t if t else 0.0
            spfm_metric = 1 - spf / t if t else 0.0
            lpfm_metric = 1 - lpf / t if t else 0.0
            thresh = ASIL_TARGETS.get(vals["asil"], ASIL_TARGETS["QM"])
            vals.update(
                {
                    "dc": dc,
                    "spfm_metric": spfm_metric,
                    "lpfm_metric": lpfm_metric,
                    "ok_dc": dc >= thresh["dc"],
                    "ok_spfm": spfm_metric >= thresh["spfm"],
                    "ok_lpfm": lpfm_metric >= thresh["lpfm"],
                }
            )
        dc_total = (total - (spf_total + lpf_total)) / total if total else 0.0
        spfm_metric_total = 1 - spf_total / total if total else 0.0
        lpfm_metric_total = 1 - lpf_total / total if total else 0.0
        thresh_total = ASIL_TARGETS.get(asil, ASIL_TARGETS["QM"])
        app.reliability_total_fit = total
        app.reliability_dc = dc_total
        app.spfm = spf_total
        app.lpfm = lpf_total
        return {
            "total": total,
            "spfm_raw": spf_total,
            "lpfm_raw": lpf_total,
            "dc": dc_total,
            "spfm_metric": spfm_metric_total,
            "lpfm_metric": lpfm_metric_total,
            "asil": asil,
            "ok_dc": dc_total >= thresh_total["dc"],
            "ok_spfm": spfm_metric_total >= thresh_total["spfm"],
            "ok_lpfm": lpfm_metric_total >= thresh_total["lpfm"],
            "goal_metrics": goal_metrics,
        }

    def sync_hara_to_safety_goals(self, app):
        sg_data = {}
        sg_asil = {}
        toolbox = getattr(app, "safety_toolbox", None)
        for doc in getattr(app, "hara_docs", []):
            approved = getattr(doc, "approved", False) or getattr(doc, "status", "") == "closed"
            for e in doc.entries:
                mal = getattr(e, "malfunction", "")
                if not mal:
                    continue
                data = sg_data.setdefault(
                    mal,
                    {"asil": "QM", "severity": 1, "cont": 1, "exp": 1, "sg": "", "approved": False},
                )
                if ASIL_ORDER.get(e.asil, 0) > ASIL_ORDER.get(data["asil"], 0):
                    data["asil"] = e.asil
                    data["sg"] = e.safety_goal
                if e.severity > data["severity"]:
                    data["severity"] = e.severity
                if e.controllability > data["cont"]:
                    data["cont"] = e.controllability
                if e.exposure > data["exp"]:
                    data["exp"] = e.exposure
                if approved:
                    data["approved"] = True
                if e.safety_goal and (
                    not toolbox
                    or toolbox.can_propagate(
                        "Risk Assessment",
                        "Product Goal Specification",
                        reviewed=approved,
                        joint_review=approved,
                    )
                ):
                    best = sg_asil.get(e.safety_goal, "QM")
                    if ASIL_ORDER.get(e.asil, 0) > ASIL_ORDER.get(best, 0):
                        sg_asil[e.safety_goal] = e.asil
        for te in app.top_events:
            mal = getattr(te, "malfunction", "")
            data = sg_data.get(mal)
            if data:
                propagate = False
                if (
                    not toolbox
                    or toolbox.can_propagate(
                        "Risk Assessment",
                        "FTA",
                        reviewed=data.get("approved", False),
                        joint_review=data.get("approved", False),
                    )
                ):
                    if getattr(te, "status", "draft") != "closed":
                        propagate = True
                    elif data.get("approved"):
                        propagate = True
                        te.status = "draft"
                        app.invalidate_reviews_for_fta(te.unique_id)
                if propagate:
                    te.safety_goal_description = data["sg"]
                    te.severity = data["severity"]
                    te.controllability = data["cont"]
                    te.exposure = data["exp"]
                    te.update_validation_target()
            sg_name = te.safety_goal_description
            asil = sg_asil.get(sg_name)
            flag = data.get("approved", False) if data else False
            if toolbox and not toolbox.can_propagate(
                "FTA", "Product Goal Specification", reviewed=flag, joint_review=flag
            ):
                asil = None
            if asil and ASIL_ORDER.get(asil, 0) > ASIL_ORDER.get(te.safety_goal_asil or "QM", 0):
                te.safety_goal_asil = asil

    def sync_cyber_risk_to_goals(self, app):
        goal_map = {g.goal_id: g for g in getattr(app, "cybersecurity_goals", [])}
        for g in goal_map.values():
            g.risk_assessments = []
        for doc in getattr(app, "hara_docs", []):
            for e in getattr(doc, "entries", []):
                cyber = getattr(e, "cyber", None)
                if not cyber or not cyber.cybersecurity_goal:
                    continue
                cg = goal_map.get(cyber.cybersecurity_goal)
            if cg is not None:
                cg.risk_assessments.append({"name": doc.name, "cal": cyber.cal})
        for g in goal_map.values():
            g.compute_cal()

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------

    def open_hazop_window(self, app):
        if hasattr(app, "_hazop_tab") and app._hazop_tab.winfo_exists():
            app.doc_nb.select(app._hazop_tab)
        else:
            app._hazop_tab = app._new_tab("HAZOP")
            app._hazop_window = HazopWindow(app._hazop_tab, app)
        app.refresh_all()

    def open_risk_assessment_window(self, app):
        if hasattr(app, "_risk_tab") and app._risk_tab.winfo_exists():
            app.doc_nb.select(app._risk_tab)
        else:
            app._risk_tab = app._new_tab("Risk Assessment")
            app._risk_window = RiskAssessmentWindow(app._risk_tab, app)
        app.refresh_all()

    def open_stpa_window(self, app):
        if hasattr(app, "_stpa_tab") and app._stpa_tab.winfo_exists():
            app.doc_nb.select(app._stpa_tab)
        else:
            app._stpa_tab = app._new_tab("STPA")
            app._stpa_window = StpaWindow(app._stpa_tab, app)
        app.refresh_all()

    def open_threat_window(self, app):
        if hasattr(app, "_threat_tab") and app._threat_tab.winfo_exists():
            app.doc_nb.select(app._threat_tab)
        else:
            app._threat_tab = app._new_tab("Threat")
            app._threat_window = ThreatWindow(app._threat_tab, app)
        app.refresh_all()

    def open_causal_bayesian_network_window(self, app):
        if hasattr(app, "_cbn_tab") and app._cbn_tab.winfo_exists():
            app.doc_nb.select(app._cbn_tab)
        else:
            app._cbn_tab = app._new_tab("Causal Bayesian Network")
            from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
            app._cbn_window = CausalBayesianNetworkWindow(app._cbn_tab, app)
        app.refresh_all()

    def open_fi2tc_window(self, app):
        if hasattr(app, "_fi2tc_tab") and app._fi2tc_tab.winfo_exists():
            app.doc_nb.select(app._fi2tc_tab)
        else:
            app._fi2tc_tab = app._new_tab("FI2TC")
            app._fi2tc_window = FI2TCWindow(app._fi2tc_tab, app)
        app.refresh_all()

    def open_tc2fi_window(self, app):
        if hasattr(app, "_tc2fi_tab") and app._tc2fi_tab.winfo_exists():
            app.doc_nb.select(app._tc2fi_tab)
        else:
            app._tc2fi_tab = app._new_tab("TC2FI")
            app._tc2fi_window = TC2FIWindow(app._tc2fi_tab, app)
        app.refresh_all()

    def show_hazard_list(self, app):
        """Open a tab to manage the list of hazards."""
        if hasattr(app, "_haz_tab") and app._haz_tab.winfo_exists():
            app.doc_nb.select(app._haz_tab)
            return
        app._haz_tab = app._new_tab("Hazards")
        win = app._haz_tab
        app.update_hazard_list()

        tree = ttk.Treeview(win, columns=("Hazard", "Severity"), show="headings")
        tree.heading("Hazard", text="Hazard")
        tree.heading("Severity", text="Severity")
        tree.column("Hazard", width=200)
        tree.column("Severity", width=80)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        class _HazardDialog(simpledialog.Dialog):
            def __init__(self, parent, title: str, name: str = "", severity: str = "1"):
                self._name = name
                self._severity = severity
                super().__init__(parent, title=title)

            def body(self, master):
                self.resizable(False, False)
                ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e")
                self.name_var = tk.StringVar(value=self._name)
                name_entry = ttk.Entry(master, textvariable=self.name_var)
                name_entry.grid(row=0, column=1, padx=5, pady=5)
                ttk.Label(master, text="Severity:").grid(row=1, column=0, sticky="e")
                self.sev_var = tk.StringVar(value=self._severity)
                ttk.Combobox(
                    master,
                    textvariable=self.sev_var,
                    values=["1", "2", "3"],
                    state="readonly",
                ).grid(row=1, column=1, padx=5, pady=5)
                return name_entry

            def apply(self):
                self.result = (
                    self.name_var.get().strip(),
                    self.sev_var.get().strip(),
                )

        def refresh():
            tree.delete(*tree.get_children())
            for h in app.hazards:
                tree.insert("", "end", values=(h, app.hazard_severity.get(h, "")))

        def add():
            dlg = _HazardDialog(win, "Add Hazard")
            if not dlg.result:
                return
            name, sev = dlg.result
            if name:
                app.add_hazard(name, sev)
                refresh()

        def rename():
            sel = tree.focus()
            if not sel:
                return
            current, sev = tree.item(sel, "values")[:2]
            dlg = _HazardDialog(win, "Edit Hazard", current, str(sev))
            if not dlg.result:
                return
            name, sev_val = dlg.result
            if name:
                if name != current:
                    app.rename_hazard(current, name)
                app.update_hazard_severity(name, sev_val)
                refresh()

        def delete():
            sel = tree.focus()
            if not sel:
                return
            current = tree.item(sel, "values")[0]
            if messagebox.askyesno("Delete", f"Delete '{current}'?"):
                app.hazards.remove(current)
                app.hazard_severity.pop(current, None)
                refresh()

        btn = ttk.Frame(win)
        btn.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Button(btn, text="Add", command=add).pack(fill=tk.X)
        ttk.Button(btn, text="Edit", command=rename).pack(fill=tk.X)
        ttk.Button(btn, text="Delete", command=delete).pack(fill=tk.X)

        refresh()

    def show_hazard_editor(self, app):
        self.show_hazard_list(app)

    def show_hazard_explorer(self, app):
        if hasattr(app, "_haz_exp_tab") and app._haz_exp_tab.winfo_exists():
            app.doc_nb.select(app._haz_exp_tab)
        else:
            app._haz_exp_tab = app._new_tab("Hazard Explorer")
            app._haz_exp_window = HazardExplorerWindow(app._haz_exp_tab, app)
            app._haz_exp_window.pack(fill=tk.BOTH, expand=True)
