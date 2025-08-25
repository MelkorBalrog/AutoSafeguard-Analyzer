from __future__ import annotations

"""Combined FTA/FMEA helper class.

This module introduces :class:`SafetyAnalysis_FTA_FMEA` which consolidates
functions for fault-tree analysis (FTA), failure mode and effects analysis
(FMEA) and FMEDA handling.  The class provides a single facade so the main
application can interact with these related analyses via one object instead of
three separate helpers.
"""

import tkinter as tk
from tkinter import filedialog, ttk
import csv

from .fta_subapp import FTASubApp
from .fmea_service import FMEAService
from .fmeda_manager import FMEDAManager


class SafetyAnalysis_FTA_FMEA(FTASubApp, FMEAService, FMEDAManager):
    """Facade combining FTA, FMEA and FMEDA behaviours."""

    def __init__(self, app: tk.Misc) -> None:
        # Initialise parent helper classes that require the application instance.
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

    # The mixins :class:`FMEAService` and :class:`FMEDAManager` already expose
    # ``fmeas`` and ``fmedas`` attributes respectively.  Previous versions of
    # this facade attempted to proxy those attributes through properties, but
    # that indirection caused the ``AttributeError`` seen when the mixins were
    # initialised.  By relying directly on the inherited attributes we avoid the
    # recursive property lookups while keeping the public interface unchanged.

