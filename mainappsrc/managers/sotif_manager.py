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

"""SOTIF management utilities for AutoMLApp."""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

from analysis.utils import (
    derive_validation_target,
    exposure_to_probability,
    controllability_to_probability,
    severity_to_probability,
)


class SOTIFManager:
    """Handle SOTIF specific helpers for :class:`AutoMLApp`.

    The manager provides small utility methods used by the main application
    to build dialogs, collect user input and derive values for Safety
    Performance Indicators (SPIs).
    """

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # ------------------------------------------------------------------
    # Dialog helpers
    # ------------------------------------------------------------------
    def build_goal_dialog(self, dlg, tab: ttk.Frame, initial) -> None:
        """Populate *tab* of the product goal dialog with SOTIF fields.

        The created Tk variables are attached to *dlg* so they can be queried
        later from :meth:`collect_goal_data`.
        """

        ttk.Label(tab, text="Acceptance Rate (1/h):").grid(row=0, column=0, sticky="e")
        dlg.accept_rate_var = tk.StringVar(value=str(getattr(initial, "acceptance_rate", 0.0)))
        tk.Entry(
            tab,
            textvariable=dlg.accept_rate_var,
            validate="key",
            validatecommand=(tab.register(dlg.app.validate_float), "%P"),
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(tab, text="On Hours:").grid(row=1, column=0, sticky="e")
        dlg.op_hours_var = tk.StringVar(value=str(getattr(initial, "operational_hours_on", 0.0)))
        tk.Entry(
            tab,
            textvariable=dlg.op_hours_var,
            validate="key",
            validatecommand=(tab.register(dlg.app.validate_float), "%P"),
        ).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(tab, text="Acceptance Criteria Description:").grid(row=2, column=0, sticky="ne")
        dlg.acc_text = tk.Text(tab, width=30, height=3, wrap="word")
        dlg.acc_text.insert("1.0", getattr(initial, "acceptance_criteria", ""))
        dlg.acc_text.grid(row=2, column=1, padx=5, pady=5)

        exp, ctrl, sev = self.probabilities_for(initial)

        ttk.Label(tab, text="P(E|HB):").grid(row=3, column=0, sticky="e")
        dlg.pehb_var = tk.StringVar(value=str(exp))
        tk.Entry(tab, textvariable=dlg.pehb_var, state="readonly").grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(tab, text="P(C|E):").grid(row=4, column=0, sticky="e")
        dlg.pce_var = tk.StringVar(value=str(ctrl))
        tk.Entry(tab, textvariable=dlg.pce_var, state="readonly").grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(tab, text="P(S|C):").grid(row=5, column=0, sticky="e")
        dlg.psc_var = tk.StringVar(value=str(sev))
        tk.Entry(tab, textvariable=dlg.psc_var, state="readonly").grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(tab, text="Validation Target (1/h):").grid(row=6, column=0, sticky="e")
        try:
            val = derive_validation_target(float(dlg.accept_rate_var.get() or 0.0), exp, ctrl, sev)
        except Exception:
            val = 1.0
        dlg.val_var = tk.StringVar(value=str(val))
        tk.Entry(tab, textvariable=dlg.val_var, state="readonly").grid(row=6, column=1, padx=5, pady=5)

        def _update_val(*_):
            try:
                acc = float(dlg.accept_rate_var.get())
                v = derive_validation_target(acc, float(dlg.pehb_var.get()), float(dlg.pce_var.get()), float(dlg.psc_var.get()))
            except Exception:
                v = 1.0
            dlg.val_var.set(str(v))

        dlg.accept_rate_var.trace_add("write", _update_val)

        ttk.Label(tab, text="Mission Profile:").grid(row=7, column=0, sticky="e")
        dlg.profile_var = tk.StringVar(value=getattr(initial, "mission_profile", ""))
        ttk.Combobox(
            tab,
            textvariable=dlg.profile_var,
            values=[mp.name for mp in self.app.mission_profiles],
            state="readonly",
        ).grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(tab, text="Val Target Description:").grid(row=8, column=0, sticky="ne")
        dlg.val_desc_text = tk.Text(tab, width=30, height=3, wrap="word")
        dlg.val_desc_text.insert("1.0", getattr(initial, "validation_desc", ""))
        dlg.val_desc_text.grid(row=8, column=1, padx=5, pady=5)

    # ------------------------------------------------------------------
    def collect_goal_data(self, dlg) -> dict[str, str]:
        """Return user input from the SOTIF section of the dialog."""
        return {
            "accept_rate": dlg.accept_rate_var.get().strip(),
            "op_hours": dlg.op_hours_var.get().strip(),
            "pehb": dlg.pehb_var.get().strip(),
            "pce": dlg.pce_var.get().strip(),
            "psc": dlg.psc_var.get().strip(),
            "val": dlg.val_var.get().strip(),
            "profile": dlg.profile_var.get().strip(),
            "val_desc": dlg.val_desc_text.get("1.0", "end-1c"),
            "accept": dlg.acc_text.get("1.0", "end-1c"),
        }

    # ------------------------------------------------------------------
    # SPI helpers
    # ------------------------------------------------------------------
    def get_spi_targets_for_goal(self, sg, pg_name: str) -> list[str]:
        """Return SPI target labels for *sg* if SOTIF data is present."""
        if getattr(sg, "validation_target", "") not in ("", None):
            return [f"{pg_name} (SOTIF)"]
        return []

    def iter_spi_rows(self):
        """Yield (sg, values) pairs for populating the SPI table."""
        for sg in getattr(self.app, "top_events", []):
            v_target = getattr(sg, "validation_target", "")
            if v_target in ("", None):
                continue
            v_str = f"{v_target:.2e}"
            sotif_prob = getattr(sg, "spi_probability", "")
            p_str = f"{sotif_prob:.2e}" if sotif_prob not in ("", None) else ""
            spi_val = ""
            try:
                if sotif_prob not in ("", None):
                    v_val = float(v_target)
                    p_val = float(sotif_prob)
                    if v_val > 0 and p_val > 0:
                        spi_val = f"{math.log10(v_val / p_val):.2f}"
            except Exception:
                spi_val = ""
            values = [
                getattr(sg, "user_name", "") or f"SG {getattr(sg, 'unique_id', '')}",
                v_str,
                p_str,
                spi_val,
                self.app._spi_label(sg),
                getattr(sg, "acceptance_criteria", ""),
            ]
            yield sg, values

    # ------------------------------------------------------------------
    def probabilities_for(self, sg) -> tuple[float, float, float]:
        """Return exposure, controllability and severity probabilities for ``sg``."""
        return (
            exposure_to_probability(getattr(sg, "exposure", 1)),
            controllability_to_probability(getattr(sg, "controllability", 1)),
            severity_to_probability(getattr(sg, "severity", 1)),
        )
