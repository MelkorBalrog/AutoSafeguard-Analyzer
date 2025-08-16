import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
import json
from config import load_report_template, validate_report_template
from gui import messagebox


class SectionDialog(simpledialog.Dialog):
    """Dialog for editing a single section."""

    def __init__(self, parent, section: dict[str, str]):
        self.section = section
        super().__init__(parent, title="Edit Section")

    def body(self, master):
        tk.Label(master, text="Title:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.title_var = tk.StringVar(value=self.section.get("title", ""))
        ttk.Entry(master, textvariable=self.title_var).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        tk.Label(master, text="Content:").grid(row=1, column=0, padx=4, pady=4, sticky="ne")
        self.content_var = tk.StringVar(value=self.section.get("content", ""))
        ttk.Entry(master, textvariable=self.content_var).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        master.columnconfigure(1, weight=1)
        return master

    def apply(self):
        self.result = {
            "title": self.title_var.get().strip(),
            "content": self.content_var.get().strip(),
        }


class ReportTemplateEditor(tk.Frame):
    """Visual editor for PDF report template configuration."""

    def __init__(self, master, app, config_path: Path | None = None):
        super().__init__(master)
        self.app = app
        self.config_path = Path(
            config_path or Path(__file__).resolve().parents[1] / "config/report_template.json"
        )
        try:
            self.data = load_report_template(self.config_path)
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror(
                "Report Template", f"Failed to load configuration:\n{exc}"
            )
            self.data = {"sections": []}

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("title",), show="headings")
        self.tree.heading("title", text="Section Title")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._edit_section)
        self.tree.grid(row=0, column=0, sticky="nsew")

        ybar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        ybar.grid(row=0, column=1, sticky="ns")

        self.preview = tk.Text(self, state="disabled", wrap="word")
        self.preview.grid(row=0, column=1, sticky="nsew")

        btn = ttk.Button(self, text="Save", command=self.save)
        btn.grid(row=1, column=1, sticky="e", padx=4, pady=4)

        self._populate_tree()

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children(""))
        for idx, sec in enumerate(self.data.get("sections", [])):
            self.tree.insert("", "end", f"sec|{idx}", values=(sec.get("title", ""),))

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0].split("|", 1)[1])
        section = self.data["sections"][idx]
        self.preview.configure(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", section.get("content", ""))
        self.preview.configure(state="disabled")

    def _edit_section(self, _event=None):
        item = self.tree.focus()
        if not item:
            return
        idx = int(item.split("|", 1)[1])
        section = self.data["sections"][idx]
        dlg = SectionDialog(self, section)
        if dlg.result:
            self.data["sections"][idx] = dlg.result
            self._populate_tree()
            self.tree.selection_set(item)
            self._on_select()

    def save(self):
        try:
            validate_report_template(self.data)
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror("Report Template", str(exc))
            return
        self.config_path.write_text(json.dumps(self.data, indent=2))
