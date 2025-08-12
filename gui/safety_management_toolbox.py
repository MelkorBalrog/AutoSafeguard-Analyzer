import json
import tkinter as tk
from tkinter import ttk, filedialog
from dataclasses import asdict
from analysis.safety_management import (
    SafetyWorkProduct,
    LifecyclePhase,
    Workflow,
    SafetyGovernance,
)


class SafetyManagementToolbox(tk.Frame):
    """UI to tailor safety work products and workflows."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.governance = SafetyGovernance()

        # --- Work Product Section ---
        wp_frame = ttk.LabelFrame(self, text="Work Products")
        wp_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(wp_frame, text="Phase:").grid(row=0, column=0, sticky="e")
        ttk.Label(wp_frame, text="Name:").grid(row=1, column=0, sticky="e")
        ttk.Label(wp_frame, text="Source:").grid(row=2, column=0, sticky="e")
        ttk.Label(wp_frame, text="Rationale:").grid(row=3, column=0, sticky="ne")

        self.phase_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.rationale_txt = tk.Text(wp_frame, width=30, height=3)

        ttk.Entry(wp_frame, textvariable=self.phase_var).grid(row=0, column=1, padx=5, pady=2)
        ttk.Entry(wp_frame, textvariable=self.name_var).grid(row=1, column=1, padx=5, pady=2)
        ttk.Entry(wp_frame, textvariable=self.source_var).grid(row=2, column=1, padx=5, pady=2)
        self.rationale_txt.grid(row=3, column=1, padx=5, pady=2)

        ttk.Button(wp_frame, text="Add", command=self.add_work_product).grid(row=4, column=1, pady=5, sticky="e")

        columns = ("Phase", "Name", "Source", "Rationale")
        self.wp_tree = ttk.Treeview(wp_frame, columns=columns, show="headings", height=5)
        for c in columns:
            self.wp_tree.heading(c, text=c)
            self.wp_tree.column(c, width=120)
        self.wp_tree.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=5)
        wp_frame.grid_rowconfigure(5, weight=1)
        wp_frame.grid_columnconfigure(1, weight=1)

        # --- Workflow Section ---
        wf_frame = ttk.LabelFrame(self, text="Workflows")
        wf_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(wf_frame, text="Workflow Name:").grid(row=0, column=0, sticky="e")
        ttk.Label(wf_frame, text="Steps (comma separated):").grid(row=1, column=0, sticky="e")

        self.workflow_name_var = tk.StringVar()
        self.workflow_steps_var = tk.StringVar()
        ttk.Entry(wf_frame, textvariable=self.workflow_name_var).grid(row=0, column=1, padx=5, pady=2)
        ttk.Entry(wf_frame, textvariable=self.workflow_steps_var).grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(wf_frame, text="Add Workflow", command=self.add_workflow).grid(row=2, column=1, pady=5, sticky="e")

        wf_columns = ("Workflow", "Steps")
        self.wf_tree = ttk.Treeview(wf_frame, columns=wf_columns, show="headings", height=5)
        for c in wf_columns:
            self.wf_tree.heading(c, text=c)
            self.wf_tree.column(c, width=150)
        self.wf_tree.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)
        wf_frame.grid_rowconfigure(3, weight=1)
        wf_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(self, text="Export Governance", command=self.export_json).pack(pady=5, anchor="e")

    # ------------------------------------------------------------------
    def add_work_product(self):
        phase = self.phase_var.get().strip()
        name = self.name_var.get().strip()
        source = self.source_var.get().strip()
        rationale = self.rationale_txt.get("1.0", "end-1c").strip()
        if not (phase and name):
            return
        lp = next((p for p in self.governance.phases if p.name == phase), None)
        if lp is None:
            lp = LifecyclePhase(name=phase)
            self.governance.phases.append(lp)
        lp.work_products.append(SafetyWorkProduct(name=name, source=source, rationale=rationale))
        self.phase_var.set("")
        self.name_var.set("")
        self.source_var.set("")
        self.rationale_txt.delete("1.0", "end")
        self.refresh_work_products()

    def refresh_work_products(self):
        self.wp_tree.delete(*self.wp_tree.get_children())
        for phase in self.governance.phases:
            for wp in phase.work_products:
                self.wp_tree.insert("", "end", values=(phase.name, wp.name, wp.source, wp.rationale))

    def add_workflow(self):
        name = self.workflow_name_var.get().strip()
        steps = [s.strip() for s in self.workflow_steps_var.get().split(",") if s.strip()]
        if not name:
            return
        self.governance.workflows.append(Workflow(name=name, steps=steps))
        self.workflow_name_var.set("")
        self.workflow_steps_var.set("")
        self.refresh_workflows()

    def refresh_workflows(self):
        self.wf_tree.delete(*self.wf_tree.get_children())
        for wf in self.governance.workflows:
            self.wf_tree.insert("", "end", values=(wf.name, ", ".join(wf.steps)))

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(self.governance), fh, indent=2)
