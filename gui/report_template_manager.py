import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
import json

from gui import messagebox


class ReportTemplateManager(tk.Frame):
    """Manage multiple PDF report templates.

    Allows listing, creating, editing and deleting template files stored
    in ``templates_dir``.  A template is any ``*.json`` file whose name
    contains ``"template"``.
    """

    def __init__(self, master, app, templates_dir: Path | None = None):
        super().__init__(master)
        self.app = app
        self.templates_dir = Path(
            templates_dir or Path(__file__).resolve().parents[1] / "config"
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(self)
        self.listbox.grid(row=0, column=0, sticky="nsew")

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=1, sticky="ns")
        ttk.Button(btn_frame, text="Add", command=self._add_template).pack(
            fill=tk.X, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Edit", command=self._edit_template).pack(
            fill=tk.X, padx=2, pady=2
        )
        ttk.Button(btn_frame, text="Delete", command=self._delete_template).pack(
            fill=tk.X, padx=2, pady=2
        )

        self._refresh_list()

    # ------------------------------------------------------------------
    def _template_files(self) -> list[Path]:
        return sorted(
            p
            for p in self.templates_dir.glob("*.json")
            if "template" in p.name.lower()
        )

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for p in self._template_files():
            self.listbox.insert(tk.END, p.name)

    # ------------------------------------------------------------------
    def _add_template(self):  # pragma: no cover - GUI dialog interaction
        name = simpledialog.askstring("Template", "Template name:")
        if not name:
            return
        if not name.lower().endswith("_template"):
            name = f"{name}_template"
        path = self.templates_dir / f"{name}.json"
        if path.exists():
            messagebox.showerror("Template", "Template already exists")
            return
        data = {"elements": {}, "sections": []}
        path.write_text(json.dumps(data, indent=2))
        self._refresh_list()

    def _selected_path(self) -> Path | None:
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.templates_dir / self.listbox.get(sel[0])

    def _edit_template(self):  # pragma: no cover - GUI dialog interaction
        path = self._selected_path()
        if not path:
            return
        from gui.report_template_toolbox import ReportTemplateEditor

        top = tk.Toplevel(self)
        editor = ReportTemplateEditor(top, self.app, path)
        editor.pack(fill=tk.BOTH, expand=True)

    def _delete_template(self):  # pragma: no cover - GUI dialog interaction
        path = self._selected_path()
        if not path:
            return
        if not messagebox.askyesno("Template", f"Delete {path.name}?"):
            return
        try:
            path.unlink()
        except Exception:
            messagebox.showerror("Template", "Failed to delete template")
            return
        self._refresh_list()
