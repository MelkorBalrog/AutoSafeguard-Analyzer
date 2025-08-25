from __future__ import annotations

"""Dialog for creating or editing global requirements.

Previously embedded within :mod:`automl_core`, this dialog is now provided as a
standalone module to keep the core application smaller and easier to maintain.
"""

import uuid
import tkinter as tk
from tkinter import ttk, simpledialog

from analysis.models import (
    ASIL_LEVEL_OPTIONS,
    CAL_LEVEL_OPTIONS,
    REQUIREMENT_TYPE_OPTIONS,
    global_requirements,
)
from gui.controls import messagebox


class ReqDialog(simpledialog.Dialog):
    """Dialog allowing users to create or modify a requirement."""

    def __init__(self, parent: tk.Widget, title: str, initial: dict | None = None):
        self.initial = initial or {}
        super().__init__(parent, title=title)

    def body(self, master: tk.Widget) -> ttk.Widget:  # type: ignore[override]
        ttk.Label(master, text="ID:").grid(row=0, column=0, sticky="e")
        self.id_var = tk.StringVar(value=self.initial.get("id", ""))
        tk.Entry(master, textvariable=self.id_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(master, text="Type:").grid(row=1, column=0, sticky="e")
        self.type_var = tk.StringVar(value=self.initial.get("req_type", "vehicle"))
        self.type_cb = ttk.Combobox(
            master,
            textvariable=self.type_var,
            values=REQUIREMENT_TYPE_OPTIONS,
            state="readonly",
            width=20,
        )
        self.type_cb.grid(row=1, column=1, padx=5, pady=5)
        self.type_cb.bind("<<ComboboxSelected>>", self._toggle_fields)

        self.asil_label = ttk.Label(master, text="ASIL:")
        self.asil_label.grid(row=2, column=0, sticky="e")
        self.asil_var = tk.StringVar(value=self.initial.get("asil", "QM"))
        self.asil_combo = ttk.Combobox(
            master,
            textvariable=self.asil_var,
            values=ASIL_LEVEL_OPTIONS,
            state="readonly",
            width=8,
        )
        self.asil_combo.grid(row=2, column=1, padx=5, pady=5)

        self.cal_label = ttk.Label(master, text="CAL:")
        self.cal_label.grid(row=3, column=0, sticky="e")
        self.cal_var = tk.StringVar(value=self.initial.get("cal", CAL_LEVEL_OPTIONS[0]))
        self.cal_combo = ttk.Combobox(
            master,
            textvariable=self.cal_var,
            values=CAL_LEVEL_OPTIONS,
            state="readonly",
            width=8,
        )
        self.cal_combo.grid(row=3, column=1, padx=5, pady=5)
        self._toggle_fields()

        ttk.Label(master, text="Parent ID:").grid(row=4, column=0, sticky="e")
        self.parent_var = tk.StringVar(value=self.initial.get("parent_id", ""))
        tk.Entry(master, textvariable=self.parent_var).grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(master, text="Status:").grid(row=5, column=0, sticky="e")
        self.status_var = tk.StringVar(value=self.initial.get("status", "draft"))
        ttk.Combobox(
            master,
            textvariable=self.status_var,
            values=["draft", "in review", "peer reviewed", "pending approval", "approved"],
            state="readonly",
        ).grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(master, text="Text:").grid(row=6, column=0, sticky="e")
        self.text_var = tk.StringVar(value=self.initial.get("text", ""))
        tk.Entry(master, textvariable=self.text_var, width=40).grid(
            row=6, column=1, padx=5, pady=5
        )
        return master

    def apply(self) -> None:  # type: ignore[override]
        rid = self.id_var.get().strip() or str(uuid.uuid4())
        req_type = self.type_var.get().strip()
        self.result = {
            "id": rid,
            "req_type": req_type,
            "parent_id": self.parent_var.get().strip(),
            "status": self.status_var.get().strip(),
            "text": self.text_var.get().strip(),
        }
        if req_type not in (
            "operational",
            "functional modification",
            "production",
            "service",
            "product",
            "legal",
            "organizational",
        ):
            self.result["asil"] = self.asil_var.get().strip()
            self.result["cal"] = self.cal_var.get().strip()

    def validate(self) -> bool:  # type: ignore[override]
        rid = self.id_var.get().strip()
        if rid and rid != self.initial.get("id") and rid in global_requirements:
            messagebox.showerror("ID", "ID already exists")
            return False
        return True

    def _toggle_fields(self, event: tk.Event | None = None) -> None:
        req_type = self.type_var.get()
        hide = req_type in (
            "operational",
            "functional modification",
            "production",
            "service",
            "product",
            "legal",
            "organizational",
        )
        widgets = [self.asil_label, self.asil_combo, self.cal_label, self.cal_combo]
        if hide:
            for w in widgets:
                w.grid_remove()
        else:
            self.asil_label.grid(row=2, column=0, sticky="e")
            self.asil_combo.grid(row=2, column=1, padx=5, pady=5)
            self.cal_label.grid(row=3, column=0, sticky="e")
            self.cal_combo.grid(row=3, column=1, padx=5, pady=5)


__all__ = ["ReqDialog"]
