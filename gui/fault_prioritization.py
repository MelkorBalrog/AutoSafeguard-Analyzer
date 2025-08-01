# SPDX-License-Identifier: GPL-3.0-or-later
"""Fault Prioritization Toolbox for AutoML.

A simplified Tkinter-based version of the PyQt GUI defined in ``faults_gui.py``.
It integrates with the main application by opening as a tab and allows mapping
faults to existing operational, technical safety and functional modification
requirements. Metrics are automatically recomputed when a cell is edited.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Dict, Any
import csv

from gui.toolboxes import EditableTreeview, configure_table_style, stripe_rows
from analysis.models import global_requirements

# Reuse the scoring dictionaries from the PyQt implementation
IMPACT_SCORES = {"None": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}
PROBABILITY_SCORES = {"Low": 1, "Medium": 2, "High": 3}
RECOVERY_SCORES = {
    "Auto-resolvable": 0,
    "Manual intervention": 1,
    "Restart required": 2,
    "Not recoverable": 3,
}
DETECTABILITY_SCORES = {"High": 0, "Medium": 1, "Low": 2}

STOP_MULTIPLIER_BY_IMPACT = {k: v / 4 for k, v in IMPACT_SCORES.items()}
STOP_MULTIPLIER_BY_RECOVERY = {
    "Auto-resolvable": 0.05,
    "Manual intervention": 0.25,
    "Restart required": 0.6,
    "Not recoverable": 1.0,
}

INPUT_COLUMNS = [
    "Fault ID",
    "Description",
    "System",
    "Probability",
    "Mission Impact",
    "Recovery",
    "Detectability",
    "Safety Critical",
    "Time To Recover (s)",
    "Occurrences /100 missions",
    "Operational Requirement",
    "Technical Safety Requirement",
    "Functional Modification",
]

OUTPUT_COLUMNS = [
    "Severity (0-5)",
    "Expected Stops /100",
    "Implementation Priority",
]

ALL_COLUMNS = INPUT_COLUMNS + OUTPUT_COLUMNS

SEVERITY_HI_TH = 4.0
SEVERITY_MED_TH = 3.0
STOPS_HI = 2.0
STOPS_MED = 0.5

W_IMPACT = 2.0
W_PROB = 1.5
W_RECOV = 1.75
W_DETECT = 1.0
W_SAFETY = 1.5


def requirement_ids(req_type: str) -> List[str]:
    return sorted(r["id"] for r in global_requirements.values() if r.get("req_type") == req_type)


def compute_metrics(row: Dict[str, Any], sev_hi: float, sev_med: float, st_hi: float, st_med: float) -> Dict[str, Any]:
    impact_cat = str(row.get("Mission Impact", "Medium"))
    prob_cat = str(row.get("Probability", "Medium"))
    recov_cat = str(row.get("Recovery", "Manual intervention"))
    detect_cat = str(row.get("Detectability", "Medium"))
    safety = bool(row.get("Safety Critical", False))
    ttr = float(row.get("Time To Recover (s)", 0) or 0)
    occ = float(row.get("Occurrences /100 missions", 0) or 0)

    impact_score = IMPACT_SCORES.get(impact_cat, 0)
    prob_score = PROBABILITY_SCORES.get(prob_cat, 1)
    recov_score = RECOVERY_SCORES.get(recov_cat, 0)
    detect_score = DETECTABILITY_SCORES.get(detect_cat, 1)

    raw = W_IMPACT * impact_score + W_PROB * prob_score + W_RECOV * recov_score + W_DETECT * detect_score
    if safety:
        raw += W_SAFETY
    max_raw = (
        W_IMPACT * 4
        + W_PROB * 3
        + W_RECOV * 3
        + W_DETECT * 2
        + W_SAFETY
    )
    severity = 0.0 if max_raw <= 0 else 5.0 * (raw / max_raw)
    severity = max(0.0, min(5.0, severity))

    stop_mult = STOP_MULTIPLIER_BY_IMPACT.get(impact_cat, 0.5) * STOP_MULTIPLIER_BY_RECOVERY.get(recov_cat, 0.5)
    ttr_penalty = 1.0 + min(2.0, (ttr / 300.0))
    expected_stops = max(0.0, occ * stop_mult) * ttr_penalty

    priority = "Low"
    if safety and impact_cat in ("High", "Critical"):
        priority = "High"
    elif severity >= sev_hi or expected_stops >= st_hi:
        priority = "High"
    elif severity >= sev_med or expected_stops >= st_med:
        priority = "Medium"

    return {
        "Severity (0-5)": round(severity, 2),
        "Expected Stops /100": round(expected_stops, 3),
        "Implementation Priority": priority,
    }


def default_rows() -> List[Dict[str, Any]]:
    base = [
        {
            "Fault ID": "F001",
            "Description": "LIDAR frame drop / data loss",
            "System": "Perception",
            "Probability": "Medium",
            "Mission Impact": "High",
            "Recovery": "Restart required",
            "Detectability": "High",
            "Safety Critical": True,
            "Time To Recover (s)": 90,
            "Occurrences /100 missions": 0.8,
            "Operational Requirement": "",
            "Technical Safety Requirement": "",
            "Functional Modification": "",
        },
        {
            "Fault ID": "F002",
            "Description": "CAN bus timeout",
            "System": "Control",
            "Probability": "Low",
            "Mission Impact": "Critical",
            "Recovery": "Not recoverable",
            "Detectability": "Medium",
            "Safety Critical": True,
            "Time To Recover (s)": 600,
            "Occurrences /100 missions": 0.2,
            "Operational Requirement": "",
            "Technical Safety Requirement": "",
            "Functional Modification": "",
        },
        {
            "Fault ID": "F003",
            "Description": "Low battery alert",
            "System": "Powertrain",
            "Probability": "High",
            "Mission Impact": "Medium",
            "Recovery": "Manual intervention",
            "Detectability": "High",
            "Safety Critical": False,
            "Time To Recover (s)": 300,
            "Occurrences /100 missions": 3.0,
            "Operational Requirement": "",
            "Technical Safety Requirement": "",
            "Functional Modification": "",
        },
        {
            "Fault ID": "F004",
            "Description": "Door sensor stuck",
            "System": "Body/Cabin",
            "Probability": "Medium",
            "Mission Impact": "Low",
            "Recovery": "Auto-resolvable",
            "Detectability": "High",
            "Safety Critical": False,
            "Time To Recover (s)": 5,
            "Occurrences /100 missions": 1.2,
            "Operational Requirement": "",
            "Technical Safety Requirement": "",
            "Functional Modification": "",
        },
    ]

    for row in base:
        row.update(compute_metrics(row, SEVERITY_HI_TH, SEVERITY_MED_TH, STOPS_HI, STOPS_MED))
    return base


class FaultPrioritizationWindow(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("Fault Prioritization")
            master.geometry("1000x600")
            self.pack(fill=tk.BOTH, expand=True)

        self.rows: List[Dict[str, Any]] = default_rows()

        th_frame = ttk.Frame(self)
        th_frame.pack(fill=tk.X)
        ttk.Label(th_frame, text="Severity High ≥").pack(side=tk.LEFT)
        self.sev_hi_var = tk.DoubleVar(value=SEVERITY_HI_TH)
        ttk.Spinbox(th_frame, textvariable=self.sev_hi_var, from_=0.0, to=5.0, increment=0.1, width=5, command=self.recompute_all).pack(side=tk.LEFT)
        ttk.Label(th_frame, text="Severity Med ≥").pack(side=tk.LEFT, padx=(10,0))
        self.sev_med_var = tk.DoubleVar(value=SEVERITY_MED_TH)
        ttk.Spinbox(th_frame, textvariable=self.sev_med_var, from_=0.0, to=5.0, increment=0.1, width=5, command=self.recompute_all).pack(side=tk.LEFT)
        ttk.Label(th_frame, text="Stops High ≥").pack(side=tk.LEFT, padx=(10,0))
        self.stops_hi_var = tk.DoubleVar(value=STOPS_HI)
        ttk.Spinbox(th_frame, textvariable=self.stops_hi_var, from_=0.0, to=50.0, increment=0.1, width=5, command=self.recompute_all).pack(side=tk.LEFT)
        ttk.Label(th_frame, text="Stops Med ≥").pack(side=tk.LEFT, padx=(10,0))
        self.stops_med_var = tk.DoubleVar(value=STOPS_MED)
        ttk.Spinbox(th_frame, textvariable=self.stops_med_var, from_=0.0, to=50.0, increment=0.1, width=5, command=self.recompute_all).pack(side=tk.LEFT)

        configure_table_style("FaultPrio.Treeview", rowheight=24)
        col_opts = {
            "Probability": list(PROBABILITY_SCORES.keys()),
            "Mission Impact": list(IMPACT_SCORES.keys()),
            "Recovery": list(RECOVERY_SCORES.keys()),
            "Detectability": list(DETECTABILITY_SCORES.keys()),
            "Operational Requirement": requirement_ids("operational"),
            "Technical Safety Requirement": requirement_ids("technical safety"),
            "Functional Modification": requirement_ids("functional modification"),
        }
        req_cols = {
            "Operational Requirement": "operational",
            "Technical Safety Requirement": "technical safety",
            "Functional Modification": "functional modification",
        }
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = EditableTreeview(
            table_frame,
            columns=ALL_COLUMNS,
            show="headings",
            style="FaultPrio.Treeview",
            column_options=col_opts,
            edit_callback=self.on_cell_edit,
            requirement_columns=req_cols,
            height=12,
        )
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for col in ALL_COLUMNS:
            self.tree.heading(col, text=col)
            width = 130 if col in OUTPUT_COLUMNS else 120
            self.tree.column(col, width=width)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.refresh_tree()

        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text="Add Row", command=self.add_row).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(btn, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2, pady=2)

        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.rows:
            values = [row.get(c, "") for c in ALL_COLUMNS]
            self.tree.insert("", "end", values=values)
        stripe_rows(self.tree)

    def recompute_all(self):
        for idx, row in enumerate(self.rows):
            self.rows[idx].update(
                compute_metrics(
                    row,
                    self.sev_hi_var.get(),
                    self.sev_med_var.get(),
                    self.stops_hi_var.get(),
                    self.stops_med_var.get(),
                )
            )
        self.refresh_tree()

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        if row >= len(self.rows):
            return
        cur = self.rows[row]
        if column in ("Time To Recover (s)", "Occurrences /100 missions"):
            try:
                cur[column] = float(value)
            except ValueError:
                cur[column] = 0.0
        elif column == "Safety Critical":
            cur[column] = value.lower() in ("1", "true", "yes")
        else:
            cur[column] = value
        cur.update(
            compute_metrics(
                cur,
                self.sev_hi_var.get(),
                self.sev_med_var.get(),
                self.stops_hi_var.get(),
                self.stops_med_var.get(),
            )
        )
        self.refresh_tree()

    def add_row(self):
        idx = len(self.rows) + 1
        row = {c: "" for c in ALL_COLUMNS}
        row.update({
            "Fault ID": f"F{idx:03d}",
            "Probability": "Medium",
            "Mission Impact": "Medium",
            "Recovery": "Manual intervention",
            "Detectability": "Medium",
            "Safety Critical": False,
            "Time To Recover (s)": 0.0,
            "Occurrences /100 missions": 0.0,
        })
        row.update(compute_metrics(row, self.sev_hi_var.get(), self.sev_med_var.get(), self.stops_hi_var.get(), self.stops_med_var.get()))
        self.rows.append(row)
        self.refresh_tree()
        self.tree.see(self.tree.get_children()[-1])

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        indices = sorted((self.tree.index(i) for i in sel), reverse=True)
        for idx in indices:
            del self.rows[idx]
        self.refresh_tree()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(ALL_COLUMNS)
            for row in self.rows:
                writer.writerow([row.get(c, "") for c in ALL_COLUMNS])



