import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
from config import load_requirement_patterns, validate_requirement_patterns
from gui import messagebox


class PatternConfig(tk.Toplevel):
    """Dialog for editing a requirement pattern's fields."""

    def __init__(self, master, pattern: dict):
        super().__init__(master)
        self.title("Edit Requirement Pattern")
        self.pattern = pattern
        self.result: dict | None = None

        self.columnconfigure(1, weight=1)

        self.pid_var = tk.StringVar(value=pattern.get("Pattern ID", ""))
        self.trigger_var = tk.StringVar(value=pattern.get("Trigger", ""))
        self.template_var = tk.StringVar(value=pattern.get("Template", ""))
        self.vars_var = tk.StringVar(
            value=", ".join(pattern.get("Variables", []))
        )
        self.notes_var = tk.StringVar(value=pattern.get("Notes", ""))

        row = 0
        tk.Label(self, text="Pattern ID:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.pid_var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=4
        )
        row += 1

        tk.Label(self, text="Trigger:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.trigger_var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=4
        )
        row += 1

        tk.Label(self, text="Template:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.template_var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=4
        )
        row += 1

        tk.Label(self, text="Variables:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.vars_var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=4
        )
        row += 1

        tk.Label(self, text="Notes:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.notes_var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=4
        )
        row += 1

        btns = ttk.Frame(self)
        btns.grid(row=row, column=0, columnspan=2, pady=4)
        ttk.Button(btns, text="OK", command=self._on_ok).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=4
        )

        self.transient(master)
        self.grab_set()

    def _on_ok(self) -> None:
        self.result = {
            "Pattern ID": self.pid_var.get().strip(),
            "Trigger": self.trigger_var.get().strip(),
            "Template": self.template_var.get().strip(),
            "Variables": [
                v.strip() for v in self.vars_var.get().split(",") if v.strip()
            ],
            "Notes": self.notes_var.get().strip(),
        }
        self.destroy()

class RequirementPatternsEditor(tk.Frame):
    """Visual editor for requirement pattern configuration."""

    def __init__(self, master, app, config_path: Path | None = None):
        super().__init__(master)
        self.app = app
        self.config_path = Path(
            config_path or Path(__file__).resolve().parents[1] / "config/requirement_patterns.json"
        )
        try:
            self.data = load_requirement_patterns(self.config_path)
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror(
                "Requirement Patterns", f"Failed to load configuration:\n{exc}"
            )
            self.data = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("trigger", "template"), show="headings")
        self.tree.heading("trigger", text="Trigger")
        self.tree.heading("template", text="Template")
        self.tree.column("trigger", width=250, stretch=True)
        self.tree.column("template", width=250, stretch=True)
        self.tree.bind("<Double-1>", self._edit_item)
        self.tree.grid(row=0, column=0, sticky="nsew")

        ybar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, sticky="e", pady=4, padx=4)
        ttk.Button(btn_frame, text="Add", command=self.add_pattern).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_pattern).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=2)

        self._populate_tree()

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children(""))
        for idx, pat in enumerate(self.data):
            trig = pat.get("Trigger", "")
            tmpl = pat.get("Template", "")
            self.tree.insert("", "end", iid=str(idx), values=(trig, tmpl))

    def _edit_item(self, _event=None):
        item = self.tree.focus()
        if not item:
            return
        idx = int(item)
        pat = self.data[idx]
        dlg = PatternConfig(self, pat)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        pat.update(dlg.result)
        self._populate_tree()

    def add_pattern(self):
        self.data.append({})
        self._populate_tree()
        self.tree.selection_set(str(len(self.data) - 1))
        self._edit_item()

    def delete_pattern(self):
        item = self.tree.focus()
        if not item:
            return
        idx = int(item)
        del self.data[idx]
        self._populate_tree()

    def save(self):
        try:
            validate_requirement_patterns(self.data)
        except ValueError as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror(
                "Requirement Patterns", f"Invalid configuration:\n{exc}"
            )
            return
        try:
            self.config_path.write_text(json.dumps(self.data, indent=2) + "\n")
            if hasattr(self.app, "reload_config"):
                self.app.reload_config()
            messagebox.showinfo("Requirement Patterns", "Configuration saved")
            self._populate_tree()
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror(
                "Requirement Patterns", f"Failed to save configuration:\n{exc}"
            )
