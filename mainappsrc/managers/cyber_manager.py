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

"""Cybersecurity utilities for AutoMLApp."""
from __future__ import annotations

import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from analysis.models import CyberRiskEntry


class CyberSecurityManager:
    """Handle cybersecurity-related operations for :class:`AutoMLApp`."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # --- Dialog helpers -------------------------------------------------
    def add_goal_dialog_fields(self, tab, goal_name: str) -> tk.StringVar:
        """Populate cybersecurity fields in the safety goal dialog.

        Returns the :class:`tk.StringVar` tracking the CAL value.
        """
        ttk.Label(tab, text="CAL:").grid(row=0, column=0, sticky="e")
        cal_var = tk.StringVar(value=self.app.get_cyber_goal_cal(goal_name))
        ttk.Label(tab, textvariable=cal_var).grid(
            row=0, column=1, padx=5, pady=5, sticky="w"
        )
        return cal_var

    # --- Risk entry handling --------------------------------------------
    def build_risk_entry(self, cdata: dict | None) -> CyberRiskEntry | None:
        """Return a :class:`CyberRiskEntry` built from *cdata* if present."""
        if not cdata:
            return None
        entry = CyberRiskEntry(
            damage_scenario=cdata.get("damage_scenario", ""),
            threat_scenario=cdata.get("threat_scenario", ""),
            attack_vector=cdata.get("attack_vector", ""),
            feasibility=cdata.get("feasibility", ""),
            financial_impact=cdata.get("financial_impact", ""),
            safety_impact=cdata.get("safety_impact", ""),
            operational_impact=cdata.get("operational_impact", ""),
            privacy_impact=cdata.get("privacy_impact", ""),
            cybersecurity_goal=cdata.get("cybersecurity_goal", ""),
        )
        entry.attack_paths = cdata.get("attack_paths", [])
        return entry

    # --- Exports --------------------------------------------------------
    def export_goal_requirements(self) -> None:
        """Export cybersecurity goals with linked risk assessments."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return

        columns = ["Cybersecurity Goal", "CAL", "Risk Assessments", "Description"]
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for cg in self.app.cybersecurity_goals:
                cg.compute_cal()
                ras = ", ".join(
                    [
                        ra.get("name", str(ra)) if isinstance(ra, dict) else str(ra)
                        for ra in cg.risk_assessments
                    ]
                )
                writer.writerow([cg.goal_id, cg.cal, ras, cg.description])
        messagebox.showinfo("Export", "Cybersecurity goal requirements exported.")
