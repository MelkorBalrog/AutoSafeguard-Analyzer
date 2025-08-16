import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
import json
from config import load_report_template, validate_report_template
from gui import messagebox


class ElementDialog(simpledialog.Dialog):
    """Dialog for adding or editing a single element placeholder."""

    def __init__(self, parent, element: dict[str, str]):
        self.element = element
        super().__init__(parent, title="Element")

    def body(self, master):
        tk.Label(master, text="Name:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.name_var = tk.StringVar(value=self.element.get("name", ""))
        ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        tk.Label(master, text="Type:").grid(row=1, column=0, padx=4, pady=4, sticky="e")
        self.type_var = tk.StringVar(value=self.element.get("type", ""))
        ttk.Entry(master, textvariable=self.type_var).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        master.columnconfigure(1, weight=1)
        return master

    def apply(self):
        self.result = {
            "name": self.name_var.get().strip(),
            "type": self.type_var.get().strip(),
        }


class ElementsDialog(simpledialog.Dialog):
    """Dialog for editing element placeholders."""

    def __init__(self, parent, elements: dict[str, str]):
        self.elements = dict(elements)
        super().__init__(parent, title="Edit Elements")

    def body(self, master):
        self.tree = ttk.Treeview(master, columns=("type",), show="headings")
        self.tree.heading("type", text="Type")
        self.tree.grid(row=0, column=0, columnspan=3, sticky="nsew")
        ybar = ttk.Scrollbar(master, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        ybar.grid(row=0, column=3, sticky="ns")

        btn_add = ttk.Button(master, text="Add", command=self._add)
        btn_add.grid(row=1, column=0, padx=2, pady=4, sticky="w")
        btn_edit = ttk.Button(master, text="Edit", command=self._edit)
        btn_edit.grid(row=1, column=1, padx=2, pady=4, sticky="w")
        btn_del = ttk.Button(master, text="Delete", command=self._delete)
        btn_del.grid(row=1, column=2, padx=2, pady=4, sticky="w")

        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self._populate()
        return master

    def _populate(self):
        self.tree.delete(*self.tree.get_children(""))
        for name, kind in sorted(self.elements.items()):
            self.tree.insert("", "end", name, values=(kind,))

    def _add(self):
        dlg = ElementDialog(self, {})
        if dlg.result:
            self.elements[dlg.result["name"]] = dlg.result["type"]
            self._populate()

    def _edit(self):
        item = self.tree.focus()
        if not item:
            return
        dlg = ElementDialog(
            self, {"name": item, "type": self.elements.get(item, "")}
        )
        if dlg.result:
            if item in self.elements:
                del self.elements[item]
            self.elements[dlg.result["name"]] = dlg.result["type"]
            self._populate()

    def _delete(self):
        item = self.tree.focus()
        if item and item in self.elements:
            del self.elements[item]
            self._populate()

    def apply(self):
        self.result = self.elements


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
        tk.Label(
            master,
            text="Use <element_name> to insert configured elements.",
        ).grid(row=2, column=0, columnspan=2, padx=4, pady=(0, 4), sticky="w")
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
            self.data = {"sections": [], "elements": {}}
        self.data.setdefault("elements", {})

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

        elem_btn = ttk.Button(self, text="Elements...", command=self._edit_elements)
        elem_btn.grid(row=1, column=0, sticky="w", padx=4, pady=4)
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

    def _edit_elements(self):
        dlg = ElementsDialog(self, self.data.get("elements", {}))
        if dlg.result is not None:
            self.data["elements"] = dlg.result

    def save(self):
        try:
            validate_report_template(self.data)
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror("Report Template", str(exc))
            return
        self.config_path.write_text(json.dumps(self.data, indent=2))
