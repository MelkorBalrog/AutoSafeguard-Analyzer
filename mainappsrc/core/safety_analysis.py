from __future__ import annotations

"""Combined FTA/FMEA helper class.

This module introduces :class:`SafetyAnalysis_FTA_FMEA` which consolidates
functions for fault-tree analysis (FTA), failure mode and effects analysis
(FMEA) and FMEDA handling.  The class provides a single facade so the main
application can interact with these related analyses via one object instead of
three separate helpers.
"""

import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
import csv

from gui.controls.mac_button_style import apply_translucid_button_style
from analysis.models import QUALIFICATIONS, COMPONENT_ATTR_TEMPLATES, component_fit_map
from analysis.fmeda_utils import GATE_NODE_TYPES, ASIL_TARGETS
from mainappsrc.models.fta.fault_tree_node import FaultTreeNode
from mainappsrc.subapps.fta_subapp import FTASubApp
from mainappsrc.core.fmea_service import FMEAService
from mainappsrc.managers.fmeda_manager import FMEDAManager


class SafetyAnalysis_FTA_FMEA(FTASubApp, FMEAService, FMEDAManager):
    """Facade combining FTA, FMEA and FMEDA behaviours."""

    def __init__(self, app: tk.Misc) -> None:
        # Internal storage for FMEA and FMEDA documents used by property
        # accessors defined later in this class.  Parent initialisers will
        # populate these via the property setters to avoid recursion.
        self._fmeas: list[dict] = []
        self._fmedas: list[dict] = []

        # Initialise parent helper classes that require the application
        # instance and make the application available to other helpers.
        FMEAService.__init__(self, app)
        FMEDAManager.__init__(self, app)
        self.app = app

    # ------------------------------------------------------------------
    # FTA convenience wrappers
    # ------------------------------------------------------------------
    def create_fta_diagram(self) -> None:
        """Initialize a new FTA diagram with a single top level event."""
        self.app._create_fta_tab("FTA")
        self.app.add_top_level_event()
        if getattr(self.app, "fta_root_node", None):
            self.app.window_controllers.open_page_diagram(self.app.fta_root_node)

    @staticmethod
    def auto_generate_fta_diagram(fta_model, output_path):
        return FTASubApp.auto_generate_fta_diagram(fta_model, output_path)

    def enable_fta_actions(self, enabled: bool) -> None:
        """Enable or disable FTA-related menu actions on the main app."""
        if hasattr(self.app, "fta_menu"):
            state = tk.NORMAL if enabled else tk.DISABLED
            for key in (
                "add_gate",
                "add_basic_event",
                "add_gate_from_failure_mode",
                "add_fault_event",
            ):
                self.app.fta_menu.entryconfig(self.app._fta_menu_indices[key], state=state)

    def show_cut_sets(self) -> None:
        """Display minimal cut sets for all top level events."""
        top_events = getattr(self.app, "top_events", [])
        if not top_events:
            return
        win = tk.Toplevel(self.app.root)
        win.title("FTA Cut Sets")
        columns = ("Top Event", "Cut Set #", "Basic Events")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for c in columns:
            tree.heading(c, text=c)
        tree.pack(fill=tk.BOTH, expand=True)

        for te in top_events:
            nodes_by_id = {}

            def map_nodes(n):
                nodes_by_id[n.unique_id] = n
                for child in n.children:
                    map_nodes(child)

            map_nodes(te)
            cut_sets = self.calculate_cut_sets(self.app, te)
            te_label = te.user_name or f"Top Event {te.unique_id}"
            for idx, cs in enumerate(cut_sets, start=1):
                names = ", ".join(
                    f"{nodes_by_id[uid].user_name or nodes_by_id[uid].node_type} [{uid}]"
                    for uid in sorted(cs)
                )
                tree.insert("", "end", values=(te_label, idx, names))
                te_label = ""

        def export_csv():
            path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV", "*.csv")]
            )
            if not path:
                return
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Top Event", "Cut Set #", "Basic Events"])
                for iid in tree.get_children():
                    writer.writerow(tree.item(iid, "values"))

        ttk.Button(win, text="Export CSV", command=export_csv).pack(pady=5)

    # ------------------------------------------------------------------
    # Delegated helpers used by existing code paths
    # ------------------------------------------------------------------
    def update_fta_statuses(self):
        return self.app.risk_app.update_fta_statuses(self.app)

    def update_basic_event_probabilities(self):
        return self.app.risk_app.update_basic_event_probabilities(self.app)

    def update_base_event_requirement_asil(self):
        return self.app.risk_app.update_base_event_requirement_asil(self.app)

    # ------------------------------------------------------------------
    # Attribute proxies
    # ------------------------------------------------------------------
    @property
    def fmeas(self) -> list[dict]:
        """Expose loaded FMEA documents."""
        return getattr(self, "_fmeas", [])

    @fmeas.setter
    def fmeas(self, value: list[dict]) -> None:
        self._fmeas = value

    @property
    def fmedas(self) -> list[dict]:
        """Expose loaded FMEDA documents."""
        return getattr(self, "_fmedas", [])

    @fmedas.setter
    def fmedas(self, value: list[dict]) -> None:
        self._fmedas = value

    # ------------------------------------------------------------------
    # FTA helpers
    # ------------------------------------------------------------------
    def _load_fault_tree_events(self, data: dict, ensure_root: bool) -> None:
        """Initialise FTA, CTA and PAA events from *data*."""
        app = self.app
        if "top_events" in data:
            app.top_events = [FaultTreeNode.from_dict(e) for e in data["top_events"]]
        elif "root_node" in data:
            root = FaultTreeNode.from_dict(data["root_node"])
            app.top_events = [root]
        else:
            app.top_events = []

        app.cta_events = [FaultTreeNode.from_dict(e) for e in data.get("cta_events", [])]
        app.paa_events = [FaultTreeNode.from_dict(e) for e in data.get("paa_events", [])]

        if (
            ensure_root
            and not app.top_events
            and "top_events" not in data
            and "root_node" not in data
        ):
            new_root = FaultTreeNode("Vehicle Level Function", "TOP EVENT")
            new_root.x, new_root.y = 300, 200
            app.top_events.append(new_root)
        app.root_node = app.top_events[0] if app.top_events else None

    def calculate_cut_sets(self, node):
        return FTASubApp.calculate_cut_sets(self, self.app, node)

    def build_simplified_fta_model(self, top_event):
        return FTASubApp.build_simplified_fta_model(self, self.app, top_event)

    def get_all_basic_events(self):
        return self.app.data_access_queries.get_all_basic_events()

    def all_children_are_base_events(self, node):
        return FTASubApp.all_children_are_base_events(self, self.app, node)

    def add_fault(self, name: str) -> None:
        self.app.risk_app.add_fault(self.app, name)

    def add_fault_event(self) -> None:
        app = self.app
        app.push_undo_state()
        dialog = app.SelectFaultDialog(app.root, sorted(app.faults), allow_new=True)
        fault = dialog.selected
        if fault == "NEW":
            fault = simpledialog.askstring("New Fault", "Name:")
            if not fault:
                return
            fault = fault.strip()
            if not fault:
                return
            self.add_fault(fault)
        if not fault:
            return
        if app.selected_node:
            parent_node = app.selected_node
            if not parent_node.is_primary_instance:
                messagebox.showwarning(
                    "Invalid Operation", "Cannot add to a clone node. Select the original."
                )
                return
        else:
            sel = app.analysis_tree.selection()
            if not sel:
                messagebox.showwarning(
                    "No selection", "Select a parent node to paste into."
                )
                return
            try:
                node_id = int(app.analysis_tree.item(sel[0], "tags")[0])
            except (IndexError, ValueError):
                messagebox.showwarning(
                    "No selection", "Select a parent node from the tree."
                )
                return
            parent_node = app.find_node_by_id_all(node_id)
        if parent_node.node_type.upper() in [
            "CONFIDENCE LEVEL",
            "ROBUSTNESS SCORE",
            "BASIC EVENT",
        ]:
            messagebox.showwarning("Invalid", "Base events cannot have children.")
            return
        new_node = FaultTreeNode("", "Basic Event", parent=parent_node)
        new_node.failure_prob = 0.0
        new_node.fault_ref = fault
        new_node.description = fault
        fit_total = 0.0
        for entry in app.get_all_fmea_entries():
            causes = [
                c.strip() for c in getattr(entry, "fmea_cause", "").split(";") if c.strip()
            ]
            if fault in causes:
                fit_total += getattr(entry, "fmeda_fit", 0.0)
                if not getattr(new_node, "prob_formula", None):
                    new_node.prob_formula = getattr(entry, "prob_formula", "linear")
        if fit_total > 0:
            new_node.fmeda_fit = fit_total
            new_node.failure_prob = app.compute_failure_prob(new_node)
        new_node.x = parent_node.x + 100
        new_node.y = parent_node.y + 100
        parent_node.children.append(new_node)
        new_node.parents.append(parent_node)
        app.update_views()

    def add_top_level_event(self) -> None:
        app = self.app
        new_event = FaultTreeNode("", "TOP EVENT")
        new_event.x, new_event.y = 300, 200
        new_event.is_top_event = True
        diag_mode = getattr(app, "diagram_mode", "FTA")
        if diag_mode == "CTA":
            app.cta_events.append(new_event)
            app.cta_root_node = new_event
            wp = "CTA"
        elif diag_mode == "PAA":
            app.paa_events.append(new_event)
            app.paa_root_node = new_event
            wp = "Prototype Assurance Analysis"
        else:
            app.top_events.append(new_event)
            app.fta_root_node = new_event
            wp = "FTA"
        app.root_node = new_event
        if hasattr(app, "safety_mgmt_toolbox"):
            app.safety_mgmt_toolbox.register_created_work_product(
                wp, new_event.user_name
            )
        app._update_shared_product_goals()
        app.update_views()

    def generate_top_event_summary(self, top_event):
        return FTASubApp.generate_top_event_summary(self, self.app, top_event)

    def generate_recommendations_for_top_event(self, node):
        return FTASubApp.generate_recommendations_for_top_event(self, self.app, node)

    def derive_requirements_for_event(self, event):
        return FTASubApp.derive_requirements_for_event(self, self.app, event)

    def get_available_failure_modes_for_gates(self, current_gate=None):
        modes = self.app.get_non_basic_failure_modes()
        used = {
            getattr(g, "failure_mode_ref", None)
            for g in self.app.get_all_gates()
            if g is not current_gate and getattr(g, "failure_mode_ref", None)
        }
        return [m for m in modes if getattr(m, "unique_id", None) not in used]

    def get_faults_for_failure_mode(self, failure_mode_node) -> list[str]:
        fm_node = self.app.get_failure_mode_node(failure_mode_node)
        fm_id = fm_node.unique_id
        faults: list[str] = []
        for be in self.get_all_basic_events():
            if getattr(be, "failure_mode_ref", None) == fm_id:
                fault = getattr(be, "fault_ref", "") or getattr(be, "description", "")
                if fault:
                    faults.append(fault)
        return sorted(set(faults))

    def get_fit_for_fault(self, fault_name: str) -> float:
        comp_fit = component_fit_map(self.app.reliability_components)
        total = 0.0
        for fm in self.app.get_all_fmea_entries():
            causes = [
                c.strip() for c in getattr(fm, "fmea_cause", "").split(";") if c.strip()
            ]
            if fault_name in causes:
                comp_name = self.app.get_component_name_for_node(fm)
                base = comp_fit.get(comp_name)
                frac = getattr(fm, "fmeda_fault_fraction", 0.0)
                if frac > 1.0:
                    frac /= 100.0
                value = base * frac if base is not None else getattr(fm, "fmeda_fit", 0.0)
                total += value
        return total

    def get_top_event(self, node):
        return FTASubApp.get_top_event(self, self.app, node)

    def move_top_event_up(self):
        return FTASubApp.move_top_event_up(self, self.app)

    def move_top_event_down(self):
        return FTASubApp.move_top_event_down(self, self.app)

    def delete_top_events_for_malfunction(self, name: str) -> None:
        app = self.app
        app.push_undo_state()
        removed = [te for te in app.top_events if getattr(te, "malfunction", "") == name]
        if not removed:
            return
        for te in removed:
            if hasattr(app, "safety_mgmt_toolbox"):
                analysis = (
                    "Prototype Assurance Analysis"
                    if getattr(app, "diagram_mode", "") == "PAA"
                    else "FTA"
                )
                app.safety_mgmt_toolbox.register_deleted_work_product(
                    analysis, te.name
                )
            app.top_events.remove(te)
            if hasattr(app, "safety_mgmt_toolbox"):
                app.safety_mgmt_toolbox.register_deleted_work_product(
                    analysis, te.user_name
                )
        if app.root_node in removed:
            app.root_node = app.top_events[0] if app.top_events else FaultTreeNode("", "TOP EVENT")
        app.update_views()

    # ------------------------------------------------------------------
    # FMEA / FMEDA helpers
    # ------------------------------------------------------------------
    def export_fmea_to_csv(self, fmea, path):
        columns = [
            "Component",
            "Parent",
            "Failure Mode",
            "Failure Effect",
            "Cause",
            "S",
            "O",
            "D",
            "RPN",
            "Requirements",
            "Malfunction",
        ]
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for be in fmea["entries"]:
                src = self.app.get_failure_mode_node(be)
                comp = self.app.get_component_name_for_node(src) or "N/A"
                parent = src.parents[0] if src.parents else None
                parent_name = (
                    parent.user_name
                    if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES
                    else ""
                )
                req_ids = "; ".join(
                    [
                        f"{req['req_type']}:{req['text']}"
                        for req in getattr(be, "safety_requirements", [])
                    ]
                )
                rpn = be.fmea_severity * be.fmea_occurrence * be.fmea_detection
                failure_mode = be.description or (be.user_name or f"BE {be.unique_id}")
                row = [
                    comp,
                    parent_name,
                    failure_mode,
                    be.fmea_effect,
                    be.fmea_cause,
                    be.fmea_severity,
                    be.fmea_occurrence,
                    be.fmea_detection,
                    rpn,
                    req_ids,
                    getattr(be, "fmeda_malfunction", ""),
                ]
                writer.writerow(row)

    def export_fmeda_to_csv(self, fmeda, path):
        columns = [
            "Component",
            "Parent",
            "Failure Mode",
            "Failure Effect",
            "Cause",
            "S",
            "O",
            "D",
            "RPN",
            "Requirements",
            "Malfunction",
            "Safety Goal",
            "FaultType",
            "Fraction",
            "FIT",
            "DiagCov",
            "Mechanism",
        ]
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for be in fmeda["entries"]:
                src = self.app.get_failure_mode_node(be)
                comp = self.app.get_component_name_for_node(src) or "N/A"
                parent = src.parents[0] if src.parents else None
                parent_name = (
                    parent.user_name
                    if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES
                    else ""
                )
                req_ids = "; ".join(
                    [
                        f"{req['req_type']}:{req['text']}"
                        for req in getattr(be, "safety_requirements", [])
                    ]
                )
                rpn = be.fmea_severity * be.fmea_occurrence * be.fmea_detection
                failure_mode = be.description or (be.user_name or f"BE {be.unique_id}")
                row = [
                    comp,
                    parent_name,
                    failure_mode,
                    be.fmea_effect,
                    be.fmea_cause,
                    be.fmea_severity,
                    be.fmea_occurrence,
                    be.fmea_detection,
                    rpn,
                    req_ids,
                    getattr(be, "fmeda_malfunction", ""),
                    ", ".join(self.app.get_top_event_safety_goals(be))
                    or getattr(be, "fmeda_safety_goal", ""),
                    getattr(be, "fmeda_fault_type", ""),
                    be.fmeda_fault_fraction,
                    be.fmeda_fit,
                    be.fmeda_diag_cov,
                    getattr(be, "fmeda_mechanism", ""),
                ]
                writer.writerow(row)

    def compute_fmeda_metrics(self, events):
        return self.app.risk_app.compute_fmeda_metrics(self.app, events)

    def calculate_fmeda_metrics(self, events):
        return self.app.risk_app.calculate_fmeda_metrics(self.app, events)

    def show_fmea_list(self):
        return FMEAService.show_fmea_list(self)

    def show_fmea_table(self, fmea=None, fmeda: bool = False):
        return self.app._show_fmea_table_impl(fmea, fmeda)

    def show_fmeda_list(self):
        return FMEDAManager.show_fmeda_list(self)

