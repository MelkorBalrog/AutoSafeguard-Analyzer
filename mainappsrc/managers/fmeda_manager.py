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

import datetime
from tkinter import ttk, simpledialog
from analysis.user_config import CURRENT_USER_NAME


class FMEDAManager:
    """Manage FMEDA documents for :class:`AutoMLApp`."""

    def __init__(self, app):
        self.app = app
        self.fmedas = []
        self._fmeda_tab = None

    def add_fmeda(self, name):
        """Create a new FMEDA document named *name* and register it."""
        file_name = f"fmeda_{name}.csv"
        now = datetime.datetime.now().isoformat()
        doc = {
            "name": name,
            "entries": [],
            "file": file_name,
            "bom": "",
            "created": now,
            "author": CURRENT_USER_NAME,
            "modified": now,
            "modified_by": CURRENT_USER_NAME,
        }
        self.fmedas.append(doc)
        toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
        if toolbox:
            toolbox.register_created_work_product("FMEDA", doc["name"])
        self.app.update_views()
        return doc

    def delete_fmeda(self, doc):
        """Remove *doc* from the FMEDA list and notify observers."""
        if doc in self.fmedas:
            self.fmedas.remove(doc)
            toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
            if toolbox:
                toolbox.register_deleted_work_product("FMEDA", doc["name"])
            self.app.update_views()

    def rename_fmeda(self, doc, name):
        """Rename *doc* to *name* and update metadata."""
        old = doc["name"]
        doc["name"] = name
        toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
        if toolbox:
            toolbox.rename_document("FMEDA", old, name)
        self.app.touch_doc(doc)
        self.app.update_views()

    def propagate_failure_mode_attributes(self, fm_node):
        """Update basic events referencing ``fm_node`` and recompute probability."""
        for be in self.app.get_all_basic_events():
            if getattr(be, "failure_mode_ref", None) == fm_node.unique_id:
                be.fmeda_fit = fm_node.fmeda_fit
                be.fmeda_diag_cov = fm_node.fmeda_diag_cov
                # Always propagate the formula so edits take effect
                be.prob_formula = fm_node.prob_formula
                be.failure_prob = self.app.compute_failure_prob(be)

    def show_fmeda_list(self):
        """Display the FMEDA list management window."""
        if self._fmeda_tab is not None and self._fmeda_tab.winfo_exists():
            self.app.doc_nb.select(self._fmeda_tab)
            return
        self._fmeda_tab = self.app._new_tab("FMEDA List")
        win = self._fmeda_tab
        columns = ("Name", "Created", "Author", "Modified", "ModifiedBy")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for c in columns:
            tree.heading(c, text=c)
            width = 150 if c == "Name" else 120
            tree.column(c, width=width)
        tree.pack(side="left", fill="both", expand=True)

        item_map = {}
        for doc in self.fmedas:
            iid = tree.insert(
                "",
                "end",
                values=(
                    doc.get("name", ""),
                    doc.get("created", ""),
                    doc.get("author", ""),
                    doc.get("modified", ""),
                    doc.get("modified_by", ""),
                ),
            )
            item_map[iid] = doc

        def open_selected(event=None):
            iid = tree.focus()
            d = item_map.get(iid)
            if not d:
                return
            win.destroy()
            self._fmeda_tab = None
            self.app.show_fmea_table(d, fmeda=True)

        def add():
            name = simpledialog.askstring("New FMEDA", "Enter FMEDA name:")
            if name:
                doc = self.add_fmeda(name)
                iid = tree.insert(
                    "",
                    "end",
                    values=(
                        doc["name"],
                        doc["created"],
                        doc["author"],
                        doc["modified"],
                        doc["modified_by"],
                    ),
                )
                item_map[iid] = doc

        def delete():
            iid = tree.focus()
            d = item_map.get(iid)
            if not d:
                return
            self.delete_fmeda(d)
            tree.delete(iid)
            item_map.pop(iid, None)

        def rename():
            iid = tree.focus()
            d = item_map.get(iid)
            if not d:
                return
            current = d.get("name", "")
            name = simpledialog.askstring(
                "Rename FMEDA", "Enter new name:", initialvalue=current
            )
            if not name:
                return
            self.rename_fmeda(d, name)
            tree.item(
                iid,
                values=(
                    d["name"],
                    d["created"],
                    d["author"],
                    d["modified"],
                    d["modified_by"],
                ),
            )

        tree.bind("<Double-1>", open_selected)
        btn_frame = ttk.Frame(win)
        btn_frame.pack(side="right", fill="y")
        ttk.Button(btn_frame, text="Open", command=open_selected).pack(fill="x")
        ttk.Button(btn_frame, text="Add", command=add).pack(fill="x")
        ttk.Button(btn_frame, text="Rename", command=rename).pack(fill="x")
        ttk.Button(btn_frame, text="Delete", command=delete).pack(fill="x")
