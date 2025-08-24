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

from analysis.models import ASIL_ORDER, ASIL_TARGETS, CAL_LEVEL_OPTIONS, component_fit_map
from analysis.utils import append_unique_insensitive
from mainappsrc.models.fta.fault_tree_node import FaultTreeNode


class RiskAssessmentSubApp:
    """Provide FMEDA calculations and risk propagation helpers."""

    def get_hazop_by_name(self, app, name):
        for d in getattr(app, "hazop_docs", []):
            if d.name == name:
                return d
        return None

    def get_hara_by_name(self, app, name):
        for d in getattr(app, "hara_docs", []):
            if d.name == name:
                return d
        return None

    def update_hara_statuses(self, app):
        """Update each risk assessment document's status based on linked reviews."""
        for doc in getattr(app, "hara_docs", []):
            status = "draft"
            for review in getattr(app, "reviews", []):
                if doc.name in getattr(review, "hara_names", []):
                    if (
                        review.mode == "joint"
                        and review.approved
                        and app.review_is_closed_for(review)
                    ):
                        status = "closed"
                        break
                    else:
                        status = "in review"
            doc.status = status
            doc.approved = status == "closed"

    def update_fta_statuses(self, app):
        """Update status for each top level event based on linked reviews."""
        for te in getattr(app, "top_events", []):
            status = "draft"
            for review in getattr(app, "reviews", []):
                if te.unique_id in getattr(review, "fta_ids", []):
                    if (
                        review.mode == "joint"
                        and review.approved
                        and app.review_is_closed_for(review)
                    ):
                        status = "closed"
                        break
                    else:
                        status = "in review"
            te.status = status

    def get_safety_goal_asil(self, app, sg_name):
        """Return the highest ASIL level for a safety goal name across approved risk assessments."""
        best = "QM"
        for doc in getattr(app, "hara_docs", []):
            if not getattr(doc, "approved", False) and getattr(doc, "status", "") != "closed":
                continue
            for e in doc.entries:
                if sg_name and sg_name == e.safety_goal and ASIL_ORDER.get(e.asil, 0) > ASIL_ORDER.get(best, 0):
                    best = e.asil
        for te in getattr(app, "top_events", []):
            if sg_name and (sg_name == te.user_name or sg_name == te.safety_goal_description):
                if ASIL_ORDER.get(te.safety_goal_asil or "QM", 0) > ASIL_ORDER.get(best, 0):
                    best = te.safety_goal_asil or "QM"
        return best

    def get_hara_goal_asil(self, app, sg_name):
        """Return highest ASIL from all risk assessment entries for the given safety goal."""
        best = "QM"
        for doc in getattr(app, "hara_docs", []):
            for e in doc.entries:
                if sg_name and sg_name == e.safety_goal and ASIL_ORDER.get(e.asil, 0) > ASIL_ORDER.get(best, 0):
                    best = e.asil
        return best

    def get_cyber_goal_cal(self, app, goal_id):
        """Return highest CAL from risk assessments for the given cybersecurity goal."""
        order = {level: idx for idx, level in enumerate(CAL_LEVEL_OPTIONS, start=1)}
        best = CAL_LEVEL_OPTIONS[0]
        for doc in getattr(app, "hara_docs", []):
            for e in getattr(doc, "entries", []):
                cyber = getattr(e, "cyber", None)
                if not cyber or not cyber.cybersecurity_goal:
                    continue
                if goal_id and goal_id == cyber.cybersecurity_goal:
                    cal = getattr(cyber, "cal", CAL_LEVEL_OPTIONS[0])
                    if order.get(cal, 0) > order.get(best, 0):
                        best = cal
        return best

    def get_top_event_safety_goals(self, app, node):
        """Return names of safety goals for top events containing ``node``."""
        result = []
        target = app.get_failure_mode_node(node)
        for te in getattr(app, "top_events", []):
            if any(n.unique_id == target.unique_id for n in app.get_all_nodes(te)):
                sg = te.safety_goal_description or te.user_name or ""
                if sg:
                    result.append(sg)
        return result

    # ------------------------------------------------------------------
    # Basic list management helpers
    # ------------------------------------------------------------------

    def _replace_in_mal_list(self, obj, old, new):
        val = getattr(obj, "fmeda_malfunction", "")
        if not val:
            return
        parts = []
        changed = False
        for m in val.split(";"):
            m = m.strip()
            if not m:
                continue
            if m == old:
                parts.append(new)
                changed = True
            else:
                parts.append(m)
        if changed:
            obj.fmeda_malfunction = ";".join(parts)

    def _replace_entry_mal(self, entry, old, new):
        val = getattr(entry, "fmeda_malfunction", "")
        if val:
            parts = [new if m.strip() == old else m.strip() for m in val.split(";") if m.strip()]
            if ";".join(parts) != val:
                entry.fmeda_malfunction = ";".join(parts)

    def _replace_name_in_list(self, value: str, old: str, new: str) -> str:
        parts = []
        changed = False
        for p in value.split(";"):
            p = p.strip()
            if not p:
                continue
            if p == old:
                parts.append(new)
                changed = True
            else:
                parts.append(p)
        return ";".join(parts) if changed else value

    def _remove_name_from_list(self, value: str, name: str) -> str:
        parts = []
        for p in value.split(";"):
            p = p.strip()
            if p and p != name:
                parts.append(p)
        return ";".join(parts)

    def add_malfunction(self, app, name: str) -> None:
        """Add a malfunction to the list if it does not already exist."""
        app.push_undo_state()
        if not name:
            return
        name = name.strip()
        if not name:
            return
        exists = any(m.lower() == name.lower() for m in app.malfunctions)
        append_unique_insensitive(app.malfunctions, name)
        if not exists and not any(getattr(te, "malfunction", "") == name for te in app.top_events):
            if len(app.top_events) == 1 and not getattr(app.top_events[0], "malfunction", ""):
                app.top_events[0].malfunction = name
                app.root_node = app.top_events[0]
                app.update_views()
            else:
                app.create_top_event_for_malfunction(name)

    def add_fault(self, app, name: str) -> None:
        """Add a fault to the list if not already present."""
        app.push_undo_state()
        append_unique_insensitive(app.faults, name)

    def add_failure(self, app, name: str) -> None:
        """Add a failure to the list if not already present."""
        app.push_undo_state()
        append_unique_insensitive(app.failures, name)

    def add_hazard(self, app, name: str, severity: int | str = 1) -> None:
        """Add a hazard to the list if not already present."""
        app.push_undo_state()
        append_unique_insensitive(app.hazards, name)
        if isinstance(severity, str):
            try:
                severity = int(severity)
            except Exception:
                severity = 1
        if name not in app.hazard_severity:
            app.hazard_severity[name] = int(severity)

    def add_triggering_condition(self, app, name: str) -> None:
        app.push_undo_state()
        name = (name or "").strip()
        if not name or name in app.triggering_conditions:
            return
        node = FaultTreeNode(name, "Triggering Condition")
        app.triggering_condition_nodes.append(node)
        if name not in app.triggering_conditions:
            app.triggering_conditions.append(name)
        app.update_triggering_condition_list()
        app.update_views()

    def delete_triggering_condition(self, app, name: str) -> None:
        app.push_undo_state()
        app.triggering_condition_nodes = [
            n for n in app.triggering_condition_nodes if n.user_name != name
        ]
        for doc in app.fi2tc_docs + app.tc2fi_docs:
            for e in doc.entries:
                val = e.get("triggering_conditions", "")
                new_val = self._remove_name_from_list(val, name)
                if new_val != val:
                    e["triggering_conditions"] = new_val
        if name in app.triggering_conditions:
            app.triggering_conditions.remove(name)
        app.update_triggering_condition_list()
        app.update_views()

    def rename_triggering_condition(self, app, old: str, new: str) -> None:
        app.push_undo_state()
        if not old or old == new:
            return
        for n in app.get_all_triggering_conditions():
            if n.user_name == old:
                n.user_name = new
        for doc in app.fi2tc_docs + app.tc2fi_docs:
            for e in doc.entries:
                val = e.get("triggering_conditions", "")
                new_val = self._replace_name_in_list(val, old, new)
                if new_val != val:
                    e["triggering_conditions"] = new_val
        if old in app.triggering_conditions:
            idx = app.triggering_conditions.index(old)
            app.triggering_conditions[idx] = new
        app.update_triggering_condition_list()
        app.update_views()

    def add_functional_insufficiency(self, app, name: str) -> None:
        app.push_undo_state()
        name = (name or "").strip()
        if not name or name in app.functional_insufficiencies:
            return
        node = FaultTreeNode(name, "Functional Insufficiency")
        node.gate_type = "AND"
        app.functional_insufficiency_nodes.append(node)
        if name not in app.functional_insufficiencies:
            app.functional_insufficiencies.append(name)
        app.update_functional_insufficiency_list()
        app.update_views()

    def delete_functional_insufficiency(self, app, name: str) -> None:
        app.push_undo_state()
        app.functional_insufficiency_nodes = [
            n for n in app.functional_insufficiency_nodes if n.user_name != name
        ]
        for doc in app.fi2tc_docs + app.tc2fi_docs:
            for e in doc.entries:
                val = e.get("functional_insufficiencies", "")
                new_val = self._remove_name_from_list(val, name)
                if new_val != val:
                    e["functional_insufficiencies"] = new_val
        if name in app.functional_insufficiencies:
            app.functional_insufficiencies.remove(name)
        app.update_functional_insufficiency_list()
        app.update_views()

    def rename_functional_insufficiency(self, app, old: str, new: str) -> None:
        app.push_undo_state()
        if not old or old == new:
            return
        for n in app.get_all_functional_insufficiencies():
            if n.user_name == old:
                n.user_name = new
        for doc in app.fi2tc_docs + app.tc2fi_docs:
            for e in doc.entries:
                val = e.get("functional_insufficiencies", "")
                new_val = self._replace_name_in_list(val, old, new)
                if new_val != val:
                    e["functional_insufficiencies"] = new_val
        if old in app.functional_insufficiencies:
            idx = app.functional_insufficiencies.index(old)
            app.functional_insufficiencies[idx] = new
        app.update_functional_insufficiency_list()
        app.update_views()

    def rename_malfunction(self, app, old: str, new: str) -> None:
        """Rename a malfunction and update all references."""
        app.push_undo_state()
        if not old or old == new:
            return
        for i, m in enumerate(app.malfunctions):
            if m == old:
                app.malfunctions[i] = new
        for te in app.top_events + getattr(app, "cta_events", []) + getattr(app, "paa_events", []):
            if getattr(te, "malfunction", "") == old:
                te.malfunction = new
        for n in app.get_all_nodes_in_model():
            self._replace_in_mal_list(n, old, new)
        for doc in app.hazop_docs:
            for e in doc.entries:
                if getattr(e, "malfunction", "") == old:
                    e.malfunction = new
        for d in app.fmeas:
            for e in d.get("entries", []):
                self._replace_entry_mal(e, old, new)
        for d in app.fmedas:
            for e in d.get("entries", []):
                self._replace_entry_mal(e, old, new)
        app.update_views()
        app._update_shared_product_goals()

    def rename_hazard(self, app, old: str, new: str) -> None:
        app.push_undo_state()
        if not old or old == new:
            return
        for i, h in enumerate(app.hazards):
            if h == old:
                app.hazards[i] = new
        if old in app.hazard_severity:
            app.hazard_severity[new] = app.hazard_severity.pop(old)
        for doc in app.hazop_docs:
            for e in doc.entries:
                if getattr(e, "hazard", "") == old:
                    e.hazard = new
        for doc in app.hara_docs:
            for e in doc.entries:
                if getattr(e, "hazard", "") == old:
                    e.hazard = new
        for doc in app.fi2tc_docs + app.tc2fi_docs:
            for e in doc.entries:
                if e.get("vehicle_effect", "") == old:
                    e["vehicle_effect"] = new
        app.update_views()

    def update_hazard_severity(self, app, hazard: str, severity: int | str) -> None:
        app.push_undo_state()
        try:
            severity = int(severity)
        except Exception:
            severity = 1
        app.hazard_severity[hazard] = severity
        for doc in app.hara_docs:
            for e in doc.entries:
                if getattr(e, "hazard", "") == hazard:
                    e.severity = severity
        for doc in app.fi2tc_docs + app.tc2fi_docs:
            for e in doc.entries:
                if e.get("vehicle_effect", "") == hazard:
                    e["severity"] = str(severity)
        app.update_views()

    def rename_fault(self, app, old: str, new: str) -> None:
        app.push_undo_state()
        if not old or old == new:
            return
        for i, f in enumerate(app.faults):
            if f == old:
                app.faults[i] = new
        for n in app.get_all_nodes_in_model():
            if getattr(n, "fault_ref", "") == old:
                n.fault_ref = new
        for be in app.get_all_fmea_entries():
            causes = [c.strip() for c in getattr(be, "fmea_cause", "").split(";")]
            changed = False
            for idx, c in enumerate(causes):
                if c == old:
                    causes[idx] = new
                    changed = True
            if changed:
                be.fmea_cause = ";".join([c for c in causes if c])
        app.update_views()

    def rename_failure(self, app, old: str, new: str) -> None:
        app.push_undo_state()
        if not old or old == new:
            return
        for i, fl in enumerate(app.failures):
            if fl == old:
                app.failures[i] = new
        for be in app.get_all_fmea_entries():
            if getattr(be, "fmea_effect", "") == old:
                be.fmea_effect = new
        for n in app.get_all_nodes_in_model():
            if getattr(n, "fmea_effect", "") == old:
                n.fmea_effect = new
        app.update_views()

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
