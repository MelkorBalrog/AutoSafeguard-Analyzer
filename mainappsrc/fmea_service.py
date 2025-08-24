"""FMEA service handling list management and dialogs."""

from __future__ import annotations

import datetime
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from analysis.user_config import CURRENT_USER_NAME
from .models.fta.fault_tree_node import FaultTreeNode


class FMEAService:
    """Service class responsible for FMEA list management."""

    def __init__(self, app: tk.Misc) -> None:
        self.app = app
        self.fmeas: list[dict] = []
        self._fmea_tab: tk.Widget | None = None

    # ------------------------------------------------------------------
    def load_fmeas(self, data: dict) -> None:
        """Load FMEA documents from project data."""
        self.fmeas.clear()
        for fmea_data in data.get("fmeas", []):
            entries = [
                FaultTreeNode.from_dict(e)
                for e in fmea_data.get("entries", [])
            ]
            self.fmeas.append(
                {
                    "name": fmea_data.get("name", "FMEA"),
                    "file": fmea_data.get("file", f"fmea_{len(self.fmeas)}.csv"),
                    "entries": entries,
                    "created": fmea_data.get(
                        "created", datetime.datetime.now().isoformat()
                    ),
                    "author": fmea_data.get("author", CURRENT_USER_NAME),
                    "modified": fmea_data.get(
                        "modified", datetime.datetime.now().isoformat()
                    ),
                    "modified_by": fmea_data.get(
                        "modified_by", CURRENT_USER_NAME
                    ),
                }
            )
        if not self.fmeas and "fmea_entries" in data:
            entries = [
                FaultTreeNode.from_dict(e) for e in data.get("fmea_entries", [])
            ]
            self.fmeas.append(
                {"name": "Default FMEA", "file": "fmea_default.csv", "entries": entries}
            )

    # ------------------------------------------------------------------
    def show_fmea_list(self) -> None:
        """Display the list of FMEA documents."""
        app = self.app
        if self._fmea_tab is not None and self._fmea_tab.winfo_exists():
            app.doc_nb.select(self._fmea_tab)
            return
        self._fmea_tab = app._new_tab("FMEA List")
        win = self._fmea_tab
        columns = ("Name", "Created", "Author", "Modified", "ModifiedBy")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for c in columns:
            tree.heading(c, text=c)
            width = 150 if c == "Name" else 120
            tree.column(c, width=width)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        item_map: dict[str, dict] = {}
        toolbox = getattr(app, "safety_mgmt_toolbox", None)
        for fmea in self.fmeas:
            name = fmea.get("name", "")
            if toolbox and not toolbox.document_visible("FMEA", name):
                continue
            iid = tree.insert(
                "",
                "end",
                values=(
                    name,
                    fmea.get("created", ""),
                    fmea.get("author", ""),
                    fmea.get("modified", ""),
                    fmea.get("modified_by", ""),
                ),
            )
            item_map[iid] = fmea

        def open_selected(event=None):
            iid = tree.focus()
            doc = item_map.get(iid)
            if not doc:
                return
            win.destroy()
            self._fmea_tab = None
            app.show_fmea_table(doc)

        def add_fmea():
            name = simpledialog.askstring("New FMEA", "Enter FMEA name:")
            if name:
                file_name = f"fmea_{name}.csv"
                now = datetime.datetime.now().isoformat()
                doc = {
                    "name": name,
                    "entries": [],
                    "file": file_name,
                    "created": now,
                    "author": CURRENT_USER_NAME,
                    "modified": now,
                    "modified_by": CURRENT_USER_NAME,
                }
                self.fmeas.append(doc)
                if hasattr(app, "safety_mgmt_toolbox"):
                    app.safety_mgmt_toolbox.register_created_work_product(
                        "FMEA", doc["name"]
                    )
                iid = tree.insert(
                    "",
                    "end",
                    values=(name, now, CURRENT_USER_NAME, now, CURRENT_USER_NAME),
                )
                item_map[iid] = doc
                app.update_views()

        def delete_fmea():
            iid = tree.focus()
            doc = item_map.get(iid)
            if not doc:
                return
            if toolbox and toolbox.document_read_only("FMEA", doc["name"]):
                messagebox.showinfo(
                    "Read-only", "Re-used FMEAs cannot be deleted"
                )
                return
            self.fmeas.remove(doc)
            if toolbox:
                toolbox.register_deleted_work_product("FMEA", doc["name"])
            tree.delete(iid)
            item_map.pop(iid, None)
            app.update_views()

        def rename_fmea():
            iid = tree.focus()
            doc = item_map.get(iid)
            if not doc:
                return
            if toolbox and toolbox.document_read_only("FMEA", doc["name"]):
                messagebox.showinfo(
                    "Read-only", "Re-used FMEAs cannot be renamed"
                )
                return
            current = doc.get("name", "")
            name = simpledialog.askstring(
                "Rename FMEA", "Enter new name:", initialvalue=current
            )
            if not name:
                return
            old = doc["name"]
            doc["name"] = name
            if toolbox:
                toolbox.rename_document("FMEA", old, name)
            app.touch_doc(doc)
            tree.item(
                iid,
                values=(
                    name,
                    doc["created"],
                    doc["author"],
                    doc["modified"],
                    doc["modified_by"],
                ),
            )
            app.update_views()

        tree.bind("<Double-1>", open_selected)
        btn_frame = ttk.Frame(win)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Button(btn_frame, text="Open", command=open_selected).pack(fill=tk.X)
        ttk.Button(btn_frame, text="Add", command=add_fmea).pack(fill=tk.X)
        ttk.Button(btn_frame, text="Rename", command=rename_fmea).pack(fill=tk.X)
        ttk.Button(btn_frame, text="Delete", command=delete_fmea).pack(fill=tk.X)

