import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
from config import (
    load_diagram_rules,
    validate_diagram_rules,
    load_requirement_patterns,
    validate_requirement_patterns,
)
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


class RuleConfig(tk.Toplevel):
    """Dialog for editing a requirement rule definition."""

    def __init__(self, master, rule: dict | None = None):
        super().__init__(master)
        rule = rule or {}
        self.title("Edit Requirement Rule")
        self.result: dict | None = None

        self.columnconfigure(1, weight=1)

        self.label_var = tk.StringVar(value=rule.get("label", ""))
        self.action_var = tk.StringVar(value=rule.get("action", ""))
        self.subject_var = tk.StringVar(value=rule.get("subject", ""))
        self.targets_var = tk.IntVar(value=rule.get("targets", 1))
        self.template_var = tk.StringVar(value=rule.get("template", ""))
        self.vars_var = tk.StringVar(
            value=", ".join(rule.get("variables", []))
        )
        self.constraint_var = tk.BooleanVar(value=rule.get("constraint", False))

        row = 0
        tk.Label(self, text="Label:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.label_var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=4
        )
        row += 1

        tk.Label(self, text="Action:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.action_var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=4
        )
        row += 1

        tk.Label(self, text="Subject:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Entry(self, textvariable=self.subject_var).grid(
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
        tk.Label(self, text="Targets:").grid(
            row=row, column=0, sticky="e", padx=4, pady=4
        )
        ttk.Spinbox(self, from_=1, to=10, textvariable=self.targets_var, width=5).grid(
            row=row, column=1, sticky="w", padx=4, pady=4
        )
        row += 1

        ttk.Checkbutton(
            self, text="Requires constraint", variable=self.constraint_var
        ).grid(row=row, column=1, sticky="w", padx=4, pady=4)
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
        label = self.label_var.get().strip()
        action = self.action_var.get().strip()
        if not label or not action:
            self.destroy()
            return
        res = {"label": label, "action": action}
        subj = self.subject_var.get().strip()
        if subj:
            res["subject"] = subj
        tmpl = self.template_var.get().strip()
        if tmpl:
            res["template"] = tmpl
            vars_ = [v.strip() for v in self.vars_var.get().split(",") if v.strip()]
            if vars_:
                res["variables"] = vars_
        tgt = self.targets_var.get()
        if tgt > 1:
            res["targets"] = tgt
        if self.constraint_var.get():
            res["constraint"] = True
        self.result = res
        self.destroy()

class RequirementPatternsEditor(tk.Frame):
    """Visual editor for requirement pattern configuration and rules."""

    def __init__(self, master, app, config_path: Path | None = None):
        super().__init__(master)
        self.app = app
        self.config_path = Path(
            config_path
            or Path(__file__).resolve().parents[1] / "config/requirement_patterns.json"
        )
        self.rules_path = (
            Path(__file__).resolve().parents[1] / "config/diagram_rules.json"
        )
        try:
            self.data = load_requirement_patterns(self.config_path)
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror(
                "Requirement Patterns", f"Failed to load configuration:\n{exc}"
            )
            self.data = []
        try:
            self.rules_cfg = load_diagram_rules(self.rules_path)
            self.req_rules = self.rules_cfg.get("requirement_rules", {})
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror(
                "Requirement Rules", f"Failed to load configuration:\n{exc}"
            )
            self.rules_cfg = {}
            self.req_rules = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")

        # ------------------------------------------------------------------
        # Patterns tab
        # ------------------------------------------------------------------
        pat_frame = ttk.Frame(nb)
        pat_frame.rowconfigure(0, weight=1)
        pat_frame.columnconfigure(0, weight=1)
        nb.add(pat_frame, text="Patterns")

        tree_frame = ttk.Frame(pat_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_frame, columns=("trigger", "template"), show="headings"
        )
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

        btn_frame = ttk.Frame(pat_frame)
        btn_frame.grid(row=1, column=0, sticky="e", pady=4, padx=4)
        ttk.Button(btn_frame, text="Add", command=self.add_pattern).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_pattern).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Save", command=self.save_patterns).pack(
            side=tk.LEFT, padx=2
        )

        # ------------------------------------------------------------------
        # Rules tab
        # ------------------------------------------------------------------
        rule_frame = ttk.Frame(nb)
        rule_frame.rowconfigure(0, weight=1)
        rule_frame.columnconfigure(0, weight=1)
        nb.add(rule_frame, text="Rules")

        r_tree_frame = ttk.Frame(rule_frame)
        r_tree_frame.grid(row=0, column=0, sticky="nsew")
        r_tree_frame.rowconfigure(0, weight=1)
        r_tree_frame.columnconfigure(0, weight=1)

        self.rule_tree = ttk.Treeview(
            r_tree_frame,
            columns=("label", "action", "subject", "template", "targets", "constraint"),
            show="headings",
        )
        for col, text in (
            ("label", "Label"),
            ("action", "Action"),
            ("subject", "Subject"),
            ("template", "Template"),
            ("targets", "Targets"),
            ("constraint", "Constraint"),
        ):
            self.rule_tree.heading(col, text=text)
            self.rule_tree.column(col, width=120, stretch=True)
        self.rule_tree.bind("<Double-1>", self._edit_rule)
        self.rule_tree.grid(row=0, column=0, sticky="nsew")

        rybar = ttk.Scrollbar(r_tree_frame, orient="vertical", command=self.rule_tree.yview)
        rxbar = ttk.Scrollbar(r_tree_frame, orient="horizontal", command=self.rule_tree.xview)
        self.rule_tree.configure(yscrollcommand=rybar.set, xscrollcommand=rxbar.set)
        rybar.grid(row=0, column=1, sticky="ns")
        rxbar.grid(row=1, column=0, sticky="ew")

        r_btn = ttk.Frame(rule_frame)
        r_btn.grid(row=1, column=0, sticky="e", pady=4, padx=4)
        ttk.Button(r_btn, text="Add", command=self.add_rule).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(r_btn, text="Delete", command=self.delete_rule).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(r_btn, text="Save", command=self.save_rules).pack(
            side=tk.LEFT, padx=2
        )

        self._populate_pattern_tree()
        self._populate_rule_tree()
        
    # ------------------------------------------------------------------
    # Pattern helpers
    # ------------------------------------------------------------------
    def _populate_pattern_tree(self):
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
        self._populate_pattern_tree()

    def add_pattern(self):
        self.data.append({})
        self._populate_pattern_tree()
        self.tree.selection_set(str(len(self.data) - 1))
        self._edit_item()

    def delete_pattern(self):
        item = self.tree.focus()
        if not item:
            return
        idx = int(item)
        del self.data[idx]
        self._populate_pattern_tree()

    def save_patterns(self):
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
            self._populate_pattern_tree()
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror(
                "Requirement Patterns", f"Failed to save configuration:\n{exc}"
            )
    # Backwards compatibility
    save = save_patterns

    # ------------------------------------------------------------------
    # Rule helpers
    # ------------------------------------------------------------------
    def _populate_rule_tree(self):
        self.rule_tree.delete(*self.rule_tree.get_children(""))
        for label, info in sorted(self.req_rules.items()):
            self.rule_tree.insert(
                "",
                "end",
                iid=label,
                values=(
                    label,
                    info.get("action", ""),
                    info.get("subject", ""),
                    info.get("template", ""),
                    info.get("targets", 1),
                    "yes" if info.get("constraint") else "",
                ),
            )

    def _edit_rule(self, _event=None):
        item = self.rule_tree.focus()
        if not item:
            return
        label = self.rule_tree.set(item, "label")
        info = dict(self.req_rules.get(label, {}))
        info["label"] = label
        dlg = RuleConfig(self, info)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        new_label = dlg.result.pop("label")
        tgt = dlg.result.pop("targets", 1)
        if label in self.req_rules:
            del self.req_rules[label]
        if tgt > 1:
            dlg.result["targets"] = tgt
        self.req_rules[new_label] = dlg.result
        self._populate_rule_tree()

    def add_rule(self):
        dlg = RuleConfig(self, {})
        self.wait_window(dlg)
        if dlg.result is None:
            return
        label = dlg.result.pop("label")
        tgt = dlg.result.pop("targets", 1)
        if tgt > 1:
            dlg.result["targets"] = tgt
        self.req_rules[label] = dlg.result
        self._populate_rule_tree()

    def delete_rule(self):
        item = self.rule_tree.focus()
        if not item:
            return
        label = self.rule_tree.set(item, "label")
        if label in self.req_rules:
            del self.req_rules[label]
        self._populate_rule_tree()

    def save_rules(self):
        self.rules_cfg["requirement_rules"] = self.req_rules
        try:
            validate_diagram_rules(self.rules_cfg)
        except ValueError as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror(
                "Requirement Rules", f"Invalid configuration:\n{exc}"
            )
            return
        try:
            self.rules_path.write_text(
                json.dumps(self.rules_cfg, indent=2) + "\n"
            )
            if hasattr(self.app, "reload_config"):
                self.app.reload_config()
            # Refresh patterns after regeneration
            try:
                self.data = load_requirement_patterns(self.config_path)
            except Exception:
                pass
            self._populate_pattern_tree()
            messagebox.showinfo("Requirement Rules", "Configuration saved")
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror(
                "Requirement Rules", f"Failed to save configuration:\n{exc}"
            )
