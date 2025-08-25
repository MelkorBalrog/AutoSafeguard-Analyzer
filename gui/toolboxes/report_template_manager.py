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

import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
from pathlib import Path
import json
import sys
import shutil

from gui.controls import messagebox


class ReportTemplateManager(tk.Frame):
    """Manage multiple PDF report templates.

    Allows listing, creating, editing and deleting template files stored
    in ``templates_dir``.  A template is any ``*.json`` file whose name
    contains ``"template"``.
    """

    @staticmethod
    def _default_templates_dir() -> Path:
        """Return base directory containing bundled report templates."""

        return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))

    @staticmethod
    def _user_templates_dir() -> Path:
        """Return directory used for user-created templates."""

        path = Path.home() / ".automl" / "templates"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def __init__(self, master, app, templates_dir: Path | None = None):
        super().__init__(master)
        self.app = app
        self.builtin_dir = Path(templates_dir or self._default_templates_dir())
        self.user_dir = self._user_templates_dir()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(self)
        self.listbox.grid(row=0, column=0, sticky="nsew")

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=1, sticky="ns")
        ttk.Button(btn_frame, text="Load", command=self._load_template).pack(
            fill=tk.X, padx=2, pady=2
        )
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
        paths = []
        for p in self.builtin_dir.rglob("*.json"):
            if "template" in p.name.lower():
                paths.append(p)
        for p in self.user_dir.rglob("*.json"):
            if "template" in p.name.lower():
                paths.append(p)

        files: dict[str, Path] = {}
        for p in paths:
            files[p.name] = p
        return [files[name] for name in sorted(files)]

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        self._name_to_path: dict[str, Path] = {}
        for p in self._template_files():
            self.listbox.insert(tk.END, p.name)
            self._name_to_path[p.name] = p

    # ------------------------------------------------------------------
    def _add_template(self):  # pragma: no cover - GUI dialog interaction
        name = simpledialog.askstring("Template", "Template name:")
        if not name:
            return
        if not name.lower().endswith("_template"):
            name = f"{name}_template"
        path = self.user_dir / f"{name}.json"
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
        name = self.listbox.get(sel[0])
        return self._name_to_path.get(name)

    def _edit_template(self):  # pragma: no cover - GUI dialog interaction
        path = self._selected_path()
        if not path:
            return
        from gui.toolboxes.report_template_toolbox import ReportTemplateEditor

        title = f"Report Template: {path.stem}"
        tab = self.app._new_tab(title)
        if tab.winfo_children():
            return
        editor = ReportTemplateEditor(tab, self.app, path)
        editor.pack(fill=tk.BOTH, expand=True)

    def _delete_template(self):  # pragma: no cover - GUI dialog interaction
        path = self._selected_path()
        if not path:
            return
        if self.user_dir not in path.parents:
            messagebox.showerror("Template", "Cannot delete bundled template")
            return
        if not messagebox.askyesno("Template", f"Delete {path.name}?"):
            return
        try:
            path.unlink()
        except Exception:
            messagebox.showerror("Template", "Failed to delete template")
            return
        self._refresh_list()

    def _load_template(self):  # pragma: no cover - GUI dialog interaction
        path = filedialog.askopenfilename(
            title="Select template", filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        src = Path(path)
        if "template" not in src.name.lower():
            messagebox.showerror("Template", "Selected file is not a template")
            return
        dest = self.user_dir / src.name
        if dest.exists():
            messagebox.showerror("Template", "Template already exists")
            return
        try:
            shutil.copy(src, dest)
        except Exception:
            messagebox.showerror("Template", "Failed to load template")
            return
        self._refresh_list()
