import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
import json
from config import load_json_with_comments
from gui import messagebox

class RequirementPatternsEditor(tk.Frame):
    """Visual editor for requirement pattern configuration."""

    def __init__(self, master, app, config_path: Path | None = None):
        super().__init__(master)
        self.app = app
        self.config_path = Path(
            config_path or Path(__file__).resolve().parents[1] / "config/requirement_patterns.json"
        )
        try:
            self.data = load_json_with_comments(self.config_path)
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
        pid = simpledialog.askstring(
            "Pattern ID", "Pattern ID", initialvalue=pat.get("Pattern ID", ""), parent=self
        )
        if pid is None:
            return
        trig = simpledialog.askstring(
            "Trigger", "Trigger", initialvalue=pat.get("Trigger", ""), parent=self
        )
        if trig is None:
            return
        tmpl = simpledialog.askstring(
            "Template", "Template", initialvalue=pat.get("Template", ""), parent=self
        )
        if tmpl is None:
            return
        vars_str = simpledialog.askstring(
            "Variables", "Comma-separated variables", initialvalue=", ".join(pat.get("Variables", [])), parent=self
        )
        if vars_str is None:
            return
        notes = simpledialog.askstring(
            "Notes", "Notes", initialvalue=pat.get("Notes", ""), parent=self
        )
        if notes is None:
            return
        pat.update(
            {
                "Pattern ID": pid.strip(),
                "Trigger": trig.strip(),
                "Template": tmpl.strip(),
                "Variables": [v.strip() for v in vars_str.split(",") if v.strip()],
                "Notes": notes.strip(),
            }
        )
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
            self.config_path.write_text(json.dumps(self.data, indent=2) + "\n")
            if hasattr(self.app, "reload_config"):
                self.app.reload_config()
            messagebox.showinfo("Requirement Patterns", "Configuration saved")
            self._populate_tree()
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror(
                "Requirement Patterns", f"Failed to save configuration:\n{exc}"
            )
