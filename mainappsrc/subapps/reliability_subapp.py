# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import annotations

"""Reliability analysis helpers separated from the main application."""

import tkinter as tk
from gui.toolboxes import ReliabilityWindow
from gui.windows.fault_prioritization import FaultPrioritizationWindow


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
