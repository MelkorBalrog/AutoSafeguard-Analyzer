from __future__ import annotations

"""Reliability analysis helpers separated from the main application."""

import tkinter as tk
from gui.toolboxes import ReliabilityWindow
from gui.fault_prioritization import FaultPrioritizationWindow


class ReliabilitySubApp:
    """Provide windows for reliability analysis and related tools."""

    def open_reliability_window(self, app):
        """Show the reliability analysis tab."""
        if hasattr(app, "_rel_tab") and app._rel_tab.winfo_exists():
            app.doc_nb.select(app._rel_tab)
        else:
            app._rel_tab = app._new_tab("Reliability")
            app._rel_window = ReliabilityWindow(app._rel_tab, app)
            app._rel_window.pack(fill=tk.BOTH, expand=True)
        app.refresh_all()

    def open_fmeda_window(self, app):
        """Open the FMEDA list view."""
        app.show_fmeda_list()
        app.refresh_all()

    def open_fault_prioritization_window(self, app):
        """Show the fault prioritization tool."""
        if hasattr(app, "_fault_prio_tab") and app._fault_prio_tab.winfo_exists():
            app.doc_nb.select(app._fault_prio_tab)
        else:
            app._fault_prio_tab = app._new_tab("Fault Prioritization")
            app._fault_prio_window = FaultPrioritizationWindow(app._fault_prio_tab, app)
        app.refresh_all()
