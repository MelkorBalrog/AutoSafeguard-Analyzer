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

from __future__ import annotations

"""Editor mixins extracted from :mod:`automl_core`.

This module provides mixin classes implementing item definition, safety
concept and requirements editor dialogs.  Extracting these helpers keeps the
main application module smaller and more maintainable.
"""

import csv
import uuid
import textwrap
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog

from analysis.models import (
    ASIL_LEVEL_OPTIONS,
    CAL_LEVEL_OPTIONS,
    REQUIREMENT_TYPE_OPTIONS,
    global_requirements,
)
from gui.controls import messagebox
from gui.dialogs.req_dialog import ReqDialog
from gui.toolboxes import DiagramElementDialog, _RequirementRelationDialog
from gui.windows.architecture import (
    link_requirement_to_object,
    unlink_requirement_from_object,
    link_requirements,
    unlink_requirements,
)
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class ItemDefinitionEditorMixin:
    """Mixin providing the item definition editor."""

    def show_item_definition_editor(self):  # pragma: no cover - UI code
        """Open editor for item description and assumptions."""
        if hasattr(self, "_item_def_tab") and self._item_def_tab.winfo_exists():
            self.doc_nb.select(self._item_def_tab)
            return
        self._item_def_tab = self.lifecycle_ui._new_tab("Item Definition")
        win = self._item_def_tab
        ttk.Label(win, text="Item Description:").pack(anchor="w")
        self._item_desc_text = tk.Text(win, height=8, wrap="word")
        self._item_desc_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(win, text="Assumptions:").pack(anchor="w")
        self._item_assum_text = tk.Text(win, height=8, wrap="word")
        self._item_assum_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._item_desc_text.insert("1.0", self.item_definition.get("description", ""))
        self._item_assum_text.insert("1.0", self.item_definition.get("assumptions", ""))

        def save() -> None:
            self.item_definition["description"] = self._item_desc_text.get("1.0", "end").strip()
            self.item_definition["assumptions"] = self._item_assum_text.get("1.0", "end").strip()

        ttk.Button(win, text="Save", command=save).pack(anchor="e", padx=5, pady=5)


class SafetyConceptEditorMixin:
    """Mixin providing the safety & security concept editor."""

    def show_safety_concept_editor(self):  # pragma: no cover - UI code
        """Open editor for safety & security concept descriptions and assumptions."""
        if hasattr(self, "_safety_concept_tab") and self._safety_concept_tab.winfo_exists():
            self.doc_nb.select(self._safety_concept_tab)
            return
        self._safety_concept_tab = self.lifecycle_ui._new_tab("Safety & Security Concept")
        win = self._safety_concept_tab
        ttk.Label(
            win,
            text="Functional & Cybersecurity Concept Description and Assumptions:",
        ).pack(anchor="w")
        f_frame = ttk.Frame(win)
        f_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._fsc_text = tk.Text(f_frame, height=8, wrap="word")
        f_scroll = ttk.Scrollbar(f_frame, orient=tk.VERTICAL, command=self._fsc_text.yview)
        self._fsc_text.configure(yscrollcommand=f_scroll.set)
        self._fsc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        f_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(
            win,
            text="Technical & Cybersecurity Concept Description & Assumptions:",
        ).pack(anchor="w")
        t_frame = ttk.Frame(win)
        t_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._tsc_text = tk.Text(t_frame, height=8, wrap="word")
        t_scroll = ttk.Scrollbar(t_frame, orient=tk.VERTICAL, command=self._tsc_text.yview)
        self._tsc_text.configure(yscrollcommand=t_scroll.set)
        self._tsc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        t_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        c_frame = ttk.Frame(win)
        c_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._csc_text = tk.Text(c_frame, height=8, wrap="word")
        c_scroll = ttk.Scrollbar(c_frame, orient=tk.VERTICAL, command=self._csc_text.yview)
        self._csc_text.configure(yscrollcommand=c_scroll.set)
        self._csc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        c_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._fsc_text.insert("1.0", self.safety_concept.get("functional", ""))
        self._tsc_text.insert("1.0", self.safety_concept.get("technical", ""))
        self._csc_text.insert("1.0", self.safety_concept.get("cybersecurity", ""))

        def save() -> None:
            self.safety_concept["functional"] = self._fsc_text.get("1.0", "end").strip()
            self.safety_concept["technical"] = self._tsc_text.get("1.0", "end").strip()
            self.safety_concept["cybersecurity"] = self._csc_text.get("1.0", "end").strip()

        ttk.Button(win, text="Save", command=save).pack(anchor="e", padx=5, pady=5)


class RequirementsEditorMixin:
    """Mixin implementing the global requirements editor."""

    def show_requirements_editor(self):  # pragma: no cover - UI heavy
        """Open an editor to manage global requirements."""
        self.update_requirement_statuses()
        if hasattr(self, "_req_tab") and self._req_tab.winfo_exists():
            self.doc_nb.select(self._req_tab)
            return
        self._req_tab = self.lifecycle_ui._new_tab("Requirements")
        win = self._req_tab

        columns = ["ID", "ASIL", "CAL", "Type", "Status", "Parent", "Trace", "Links", "Text"]
        tree_frame = ttk.Frame(win)
        style = ttk.Style(tree_frame)
        style.configure("ReqEditor.Treeview", rowheight=20)
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="ReqEditor.Treeview",
        )
        tree.configure(height=10)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for col in columns:
            tree.heading(col, text=col)
            if col == "Text":
                width = 300
            elif col in ("Trace", "Links"):
                width = 200
            else:
                width = 120
            tree.column(col, width=width, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        def _get_requirement_allocations(rid: str) -> list[str]:
            repo = SysMLRepository.get_instance()
            names: list[str] = []
            for diag in repo.diagrams.values():
                dname = diag.name or diag.diag_id
                for obj in getattr(diag, "objects", []):
                    for r in obj.get("requirements", []):
                        if r.get("id") == rid:
                            oname = obj.get("properties", {}).get("name", obj.get("obj_type"))
                            names.append(f"{dname}:{oname}")
            return sorted(set(names))

        def refresh_tree() -> None:
            tree.delete(*tree.get_children())
            max_lines = 1
            for req in global_requirements.values():
                rid = req.get("id", "")
                trace = ", ".join(_get_requirement_allocations(rid))
                links = ", ".join(
                    f"{r.get('type')} {r.get('id')}" for r in req.get("relations", [])
                )
                text = textwrap.fill(req.get("text", ""), width=40)
                max_lines = max(max_lines, text.count("\n") + 1)
                tree.insert(
                    "",
                    "end",
                    iid=rid,
                    values=[
                        rid,
                        req.get("asil", ""),
                        req.get("cal", ""),
                        req.get("req_type", ""),
                        req.get("status", "draft"),
                        req.get("parent_id", ""),
                        trace,
                        links,
                        text,
                    ],
                )
            style.configure("ReqEditor.Treeview", rowheight=20 * max_lines)

        def add_req() -> None:
            dlg = ReqDialog(win, "Add Requirement")
            if dlg.result:
                global_requirements[dlg.result["id"]] = dlg.result
                refresh_tree()

        def edit_req() -> None:
            sel = tree.selection()
            if not sel:
                return
            rid = sel[0]
            dlg = ReqDialog(win, "Edit Requirement", global_requirements.get(rid))
            if dlg.result:
                global_requirements[rid].update(dlg.result)
                refresh_tree()

        def del_req() -> None:
            sel = tree.selection()
            if not sel:
                return
            rid = sel[0]
            if messagebox.askyesno("Delete", "Delete requirement?"):
                del global_requirements[rid]
                for n in self.get_all_nodes(self.root_node):
                    reqs = getattr(n, "safety_requirements", [])
                    n.safety_requirements = [r for r in reqs if r.get("id") != rid]
                for fmea in self.fmeas:
                    for e in fmea.get("entries", []):
                        reqs = e.get("safety_requirements", [])
                        e["safety_requirements"] = [r for r in reqs if r.get("id") != rid]
                refresh_tree()

        def link_to_diagram() -> None:
            sel = tree.selection()
            if not sel:
                return
            rid = sel[0]
            req = global_requirements.get(rid)
            if not req:
                return
            repo = SysMLRepository.get_instance()
            toolbox = getattr(self, "safety_mgmt_toolbox", None)
            can_trace = toolbox.can_trace if toolbox else (lambda a, b: True)
            req_wp = (
                toolbox.requirement_work_product(req.get("req_type", ""))
                if toolbox
                else ""
            )

            # Determine currently allocated diagram objects
            existing: set[tuple[str, int]] = set()
            for diag in repo.diagrams.values():
                for obj in getattr(diag, "objects", []):
                    if any(r.get("id") == rid for r in obj.get("requirements", [])):
                        existing.add((diag.diag_id, obj.get("obj_id")))

            dlg = DiagramElementDialog(win, repo, req_wp, can_trace, selected=list(existing))
            targets = set(getattr(dlg, "selection", []))
            if not targets and not existing:
                return

            # Add newly selected links
            for diag_id, obj_id in targets - existing:
                diag = repo.diagrams.get(diag_id)
                if not diag:
                    continue
                obj = next(
                    (o for o in getattr(diag, "objects", []) if o.get("obj_id") == obj_id),
                    None,
                )
                if not obj:
                    continue
                link_requirement_to_object(obj, rid, diag_id)
                repo.touch_diagram(diag_id)
                elem_id = obj.get("element_id")
                if elem_id:
                    repo.touch_element(elem_id)

            # Remove deselected links
            for diag_id, obj_id in existing - targets:
                diag = repo.diagrams.get(diag_id)
                if not diag:
                    continue
                obj = next(
                    (o for o in getattr(diag, "objects", []) if o.get("obj_id") == obj_id),
                    None,
                )
                if not obj:
                    continue
                unlink_requirement_from_object(obj, rid, diag_id)
                repo.touch_diagram(diag_id)
                elem_id = obj.get("element_id")
                if elem_id:
                    repo.touch_element(elem_id)

            refresh_tree()

        def link_requirement() -> None:
            sel = tree.selection()
            if not sel:
                return
            rid = sel[0]
            req = global_requirements.get(rid)
            if not req:
                return
            toolbox = getattr(self, "safety_mgmt_toolbox", None)
            dlg = _RequirementRelationDialog(win, req, toolbox)
            if not dlg.result:
                return
            relation, targets = dlg.result
            selected = set(targets)
            existing = {
                r.get("id")
                for r in req.get("relations", [])
                if r.get("type") == relation
            }
            for tid in selected - existing:
                link_requirements(rid, relation, tid)
            for tid in existing - selected:
                unlink_requirements(rid, relation, tid)
            refresh_tree()

        def save_csv() -> None:
            path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV", "*.csv")]
            )
            if not path:
                return
            try:
                with open(path, "w", newline="") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(columns)
                    for req in global_requirements.values():
                        rid = req.get("id", "")
                        trace = ", ".join(_get_requirement_allocations(rid))
                        links = ", ".join(
                            f"{r.get('type')} {r.get('id')}" for r in req.get("relations", [])
                        )
                        writer.writerow(
                            [
                                rid,
                                req.get("asil", ""),
                                req.get("cal", ""),
                                req.get("req_type", ""),
                                req.get("status", "draft"),
                                req.get("parent_id", ""),
                                trace,
                                links,
                                req.get("text", ""),
                            ]
                        )
                messagebox.showinfo(
                    "Requirements", f"Saved {len(global_requirements)} requirements to {path}"
                )
            except Exception as exc:  # pragma: no cover - error path
                messagebox.showerror("Requirements", f"Failed to save CSV:\n{exc}")

        if hasattr(tree, "bind"):
            try:
                menu = tk.Menu(tree, tearoff=False)
            except Exception:  # pragma: no cover - platform specific
                menu = None
            if menu:
                menu.add_command(label="Add", command=add_req)
                menu.add_command(label="Edit", command=edit_req)
                menu.add_command(label="Delete", command=del_req)
                menu.add_command(label="Link to Diagram...", command=link_to_diagram)
                menu.add_command(label="Link Requirement...", command=link_requirement)
                menu.add_command(label="Save CSV", command=save_csv)

                def _popup(event: tk.Event) -> None:
                    row = tree.identify_row(event.y)
                    if row:
                        tree.selection_set(row)
                        tree.focus(row)
                    try:
                        menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        menu.grab_release()

                def _on_double(event: tk.Event) -> None:
                    row = tree.identify_row(event.y)
                    if row:
                        tree.selection_set(row)
                        tree.focus(row)
                        edit_req()

                tree.bind("<Button-3>", _popup)
                tree.bind("<Button-2>", _popup)
                tree.bind("<Control-Button-1>", _popup)
                tree.bind("<Double-1>", _on_double)
                tree.context_menu = menu

        btn = tk.Frame(win)
        btn.pack(fill=tk.X)
        tk.Button(btn, text="Add", command=add_req).pack(side=tk.LEFT)
        tk.Button(btn, text="Edit", command=edit_req).pack(side=tk.LEFT)
        tk.Button(btn, text="Delete", command=del_req).pack(side=tk.LEFT)
        tk.Button(btn, text="Save CSV", command=save_csv).pack(side=tk.LEFT)
        tk.Button(btn, text="Link to Diagram...", command=link_to_diagram).pack(side=tk.LEFT)
        tk.Button(btn, text="Link Requirement...", command=link_requirement).pack(side=tk.LEFT)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        refresh_tree()


__all__ = [
    "ItemDefinitionEditorMixin",
    "SafetyConceptEditorMixin",
    "RequirementsEditorMixin",
]
