from __future__ import annotations

"""Project editing helpers separated from the main application."""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

from analysis.utils import update_probability_tables
from gui import messagebox


class ProjectEditorSubApp:
    """Encapsulate project property editing behaviours."""

    def build_probability_frame(
        self,
        app,
        parent,
        title: str,
        levels: range,
        values: dict,
        row: int,
        dialog_font: tkFont.Font,
    ) -> dict:
        """Create a labelled frame of probability entries.

        Returns a mapping of level -> ``StringVar`` for the entered values.
        """
        try:
            frame = ttk.LabelFrame(parent, text=title, style="Toolbox.TLabelframe")
        except TypeError:  # pragma: no cover - style may not be initialised during tests
            frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        vars_dict: dict[int, tk.StringVar] = {}
        for idx, lvl in enumerate(levels):
            ttk.Label(frame, text=f"{lvl}:", font=dialog_font).grid(
                row=0, column=idx * 2, padx=2, pady=2
            )
            var = tk.StringVar(value=str(values.get(lvl, 0.0)))
            ttk.Entry(
                frame,
                textvariable=var,
                width=8,
                font=dialog_font,
                validate="key",
                validatecommand=(parent.register(app.validate_float), "%P"),
            ).grid(row=0, column=idx * 2 + 1, padx=2, pady=2)
            vars_dict[lvl] = var
        return vars_dict

    def apply_project_properties(
        self,
        app,
        name: str,
        detailed: bool,
        exp_vars: dict,
        ctrl_vars: dict,
        sev_vars: dict,
        smt,
        freeze: bool,
    ) -> None:
        """Persist updated project properties and refresh probability tables."""
        app.project_properties["pdf_report_name"] = name
        app.project_properties["pdf_detailed_formulas"] = detailed
        app.project_properties["exposure_probabilities"] = {
            lvl: float(var.get() or 0.0) for lvl, var in exp_vars.items()
        }
        app.project_properties["controllability_probabilities"] = {
            lvl: float(var.get() or 0.0) for lvl, var in ctrl_vars.items()
        }
        app.project_properties["severity_probabilities"] = {
            lvl: float(var.get() or 0.0) for lvl, var in sev_vars.items()
        }
        update_probability_tables(
            app.project_properties["exposure_probabilities"],
            app.project_properties["controllability_probabilities"],
            app.project_properties["severity_probabilities"],
        )
        if smt:
            app.governance_manager.freeze_governance_diagrams(freeze)

    def edit_project_properties(self, app):
        """Display dialog for editing project properties."""
        prop_win = tk.Toplevel(app.root)
        prop_win.title("Project Properties")
        prop_win.resizable(False, False)
        dialog_font = tkFont.Font(family="Arial", size=10)

        ttk.Label(prop_win, text="PDF Report Name:", font=dialog_font).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        pdf_entry = ttk.Entry(prop_win, width=40, font=dialog_font)
        pdf_entry.insert(0, app.project_properties.get("pdf_report_name", "AutoML-Analyzer PDF Report"))
        pdf_entry.grid(row=0, column=1, padx=10, pady=10)

        var_detailed = tk.BooleanVar(
            value=app.project_properties.get("pdf_detailed_formulas", True)
        )
        ttk.Checkbutton(
            prop_win,
            text="Show Detailed Formulas in PDF Report",
            variable=var_detailed,
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        smt = getattr(app, "safety_mgmt_toolbox", None)
        all_frozen = False
        if smt:
            diagrams = smt.list_diagrams()
            all_frozen = diagrams and all(smt.diagram_frozen(d) for d in diagrams)
        var_freeze = tk.BooleanVar(
            value=app.project_properties.get("freeze_governance_diagrams", bool(all_frozen))
        )
        ttk.Checkbutton(
            prop_win,
            text="Freeze Governance Diagrams",
            variable=var_freeze,
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        exp_vars = self.build_probability_frame(
            app,
            prop_win,
            "Exposure Probabilities P(E|HB)",
            range(1, 5),
            app.project_properties.get("exposure_probabilities", {}),
            3,
            dialog_font,
        )
        ctrl_vars = self.build_probability_frame(
            app,
            prop_win,
            "Controllability Probabilities P(C|E)",
            range(1, 4),
            app.project_properties.get("controllability_probabilities", {}),
            4,
            dialog_font,
        )
        sev_vars = self.build_probability_frame(
            app,
            prop_win,
            "Severity Probabilities P(S|C)",
            range(1, 4),
            app.project_properties.get("severity_probabilities", {}),
            5,
            dialog_font,
        )

        def save_props() -> None:
            new_name = pdf_entry.get().strip()
            if not new_name:
                messagebox.showwarning(
                    "Project Properties", "PDF Report Name cannot be empty."
                )
                return

            app.project_properties["pdf_report_name"] = new_name
            app.project_properties["pdf_detailed_formulas"] = var_detailed.get()
            app.project_properties["exposure_probabilities"] = {
                lvl: float(var.get() or 0.0) for lvl, var in exp_vars.items()
            }
            app.project_properties["controllability_probabilities"] = {
                lvl: float(var.get() or 0.0) for lvl, var in ctrl_vars.items()
            }
            app.project_properties["severity_probabilities"] = {
                lvl: float(var.get() or 0.0) for lvl, var in sev_vars.items()
            }
            app.project_properties["freeze_governance_diagrams"] = var_freeze.get()
            update_probability_tables(
                app.project_properties["exposure_probabilities"],
                app.project_properties["controllability_probabilities"],
                app.project_properties["severity_probabilities"],
            )
            if smt:
                app.governance_manager.freeze_governance_diagrams(var_freeze.get())
            messagebox.showinfo(
                "Project Properties", "Project properties updated."
            )
            prop_win.destroy()

        ttk.Button(prop_win, text="Save", command=save_props, width=10).grid(
            row=6, column=0, columnspan=2, pady=10
        )
        prop_win.update_idletasks()
        prop_win.minsize(prop_win.winfo_width(), prop_win.winfo_height())
        prop_win.transient(app.root)
        prop_win.grab_set()
        app.root.wait_window(prop_win)
