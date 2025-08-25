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

"""Tree-related event handlers for AutoML."""

import tkinter as tk
from tkinter import messagebox, simpledialog

try:  # pragma: no cover - support relative imports
    from mainappsrc.models.sysml.sysml_repository import SysMLRepository
except Exception:  # pragma: no cover
    SysMLRepository = None  # type: ignore


class TreeSubApp:
    """Encapsulate analysis tree operations."""

    def on_treeview_click(self, app, event):
        sel = app.analysis_tree.selection()
        if not sel:
            return
        try:
            node_id = int(app.analysis_tree.item(sel[0], "tags")[0])
        except (IndexError, ValueError):
            return
        node = app.find_node_by_id_all(node_id)
        if node:
            app.window_controllers.open_page_diagram(node)

    def on_analysis_tree_double_click(self, app, event):
        item = (
            app.analysis_tree.identify_row(event.y)
            if event is not None
            else app.analysis_tree.focus()
        )
        if not item:
            return
        app.analysis_tree.focus(item)
        tags = app.analysis_tree.item(item, "tags")
        kind = tags[0] if tags else None
        ident = tags[1] if tags and len(tags) > 1 else None
        if kind in {"fmea", "fmeda", "hazop", "hara", "stpa", "threat", "fi2tc", "tc2fi", "jrev", "gov"} and ident is not None:
            idx = int(ident)
            if kind == "fmea":
                app.show_fmea_table(app.fmeas[idx])
            elif kind == "fmeda":
                app.show_fmea_table(app.fmedas[idx], fmeda=True)
            elif kind == "hazop":
                app.open_hazop_window()
                if hasattr(app, "_hazop_window"):
                    doc = app.hazop_docs[idx]
                    app._hazop_window.doc_var.set(doc.name)
                    app._hazop_window.select_doc()
            elif kind == "hara":
                app.open_risk_assessment_window()
                if hasattr(app, "_risk_window"):
                    doc = app.hara_docs[idx]
                    app._risk_window.doc_var.set(doc.name)
                    app._risk_window.select_doc()
            elif kind == "stpa":
                app.open_stpa_window()
                if hasattr(app, "_stpa_window"):
                    doc = app.stpa_docs[idx]
                    app._stpa_window.doc_var.set(doc.name)
                    app._stpa_window.select_doc()
            elif kind == "threat":
                app.open_threat_window()
                if hasattr(app, "_threat_window"):
                    doc = app.threat_docs[idx]
                    app._threat_window.doc_var.set(doc.name)
                    app._threat_window.select_doc()
            elif kind == "fi2tc":
                app.open_fi2tc_window()
                if hasattr(app, "_fi2tc_window"):
                    doc = app.fi2tc_docs[idx]
                    app._fi2tc_window.doc_var.set(doc.name)
                    app._fi2tc_window.select_doc()
            elif kind == "tc2fi":
                app.open_tc2fi_window()
                if hasattr(app, "_tc2fi_window"):
                    doc = app.tc2fi_docs[idx]
                    app._tc2fi_window.doc_var.set(doc.name)
                    app._tc2fi_window.select_doc()
            elif kind == "jrev":
                if 0 <= idx < len(getattr(app, "joint_reviews", [])):
                    review = app.joint_reviews[idx]
                    app.review_data = review
                    app.open_review_document(review)
                    app.open_review_toolbox()
            elif kind == "gov":
                app.open_management_window(idx)
        elif kind == "gsn" and ident is not None:
            diag = getattr(app, "gsn_diagram_map", {}).get(ident)
            if diag:
                app.window_controllers.open_gsn_diagram(diag)
        elif kind == "gsnmod":
            app.manage_gsn()
        elif kind == "reqs":
            app.show_requirements_editor()
        elif kind == "reqexp":
            app.show_requirements_explorer()
        elif kind == "sg":
            app.show_product_goals_editor()
        elif kind == "fta" and ident is not None:
            te = next((t for t in app.top_events if t.unique_id == int(ident)), None)
            if te:
                app.diagram_mode = "FTA"
                app.ensure_fta_tab()
                app.doc_nb.select(app.canvas_tab)
                app.window_controllers.open_page_diagram(te)
        elif kind == "cta" and ident is not None:
            te = next((t for t in getattr(app, "cta_events", []) if t.unique_id == int(ident)), None)
            if te:
                app.diagram_mode = "CTA"
                app.ensure_fta_tab()
                app.doc_nb.select(app.canvas_tab)
                app.window_controllers.open_page_diagram(te)
        elif kind == "paa" and ident is not None:
            te = next((t for t in getattr(app, "paa_events", []) if t.unique_id == int(ident)), None)
            if te:
                app.diagram_mode = "PAA"
                app.ensure_fta_tab()
                app.doc_nb.select(app.canvas_tab)
                app.window_controllers.open_page_diagram(te)
        elif kind == "safetycase":
            app.manage_safety_cases()
        elif kind == "safetyconcept":
            app.show_safety_concept_editor()
        elif kind == "itemdef":
            app.show_item_definition_editor()
        elif kind == "arch":
            app.window_controllers.open_arch_window(ident)
        elif kind == "pkg":
            app.manage_architecture()
        else:
            parent = item
            while parent:
                if (
                    app.analysis_tree.item(parent, "text")
                    == "Safety & Security Governance Diagrams"
                ):
                    app.manage_safety_management()
                    return
                parent = app.analysis_tree.parent(parent)

    def on_analysis_tree_right_click(self, app, event):
        iid = app.analysis_tree.identify_row(event.y)
        if not iid:
            return
        app.analysis_tree.selection_set(iid)
        app.analysis_tree.focus(iid)
        menu = tk.Menu(app.analysis_tree, tearoff=0)
        menu.add_command(
            label="Rename", command=lambda: self.rename_selected_tree_item(app)
        )
        menu.tk_popup(event.x_root, event.y_root)

    def on_analysis_tree_select(self, app, _event):
        if not hasattr(app, "prop_view"):
            return
        item = app.analysis_tree.focus()
        if not item:
            return
        tags = app.analysis_tree.item(item, "tags")
        name = app.analysis_tree.item(item, "text")
        meta = {"Name": name}
        if tags:
            meta["Type"] = tags[0]
            if len(tags) > 1:
                ident = tags[1]
                meta["ID"] = ident
                if SysMLRepository:
                    repo = SysMLRepository.get_instance()
                    elem = repo.elements.get(ident)
                    if elem:
                        meta.update(
                            {
                                "Type": elem.elem_type,
                                "Author": getattr(elem, "author", ""),
                                "Created": getattr(elem, "created", ""),
                                "Modified": getattr(elem, "modified", ""),
                                "ModifiedBy": getattr(elem, "modified_by", ""),
                            }
                        )
                    else:
                        diag = repo.diagrams.get(ident)
                        if diag:
                            meta.update(
                                {
                                    "Type": diag.diag_type,
                                    "Author": getattr(diag, "author", ""),
                                    "Created": getattr(diag, "created", ""),
                                    "Modified": getattr(diag, "modified", ""),
                                    "ModifiedBy": getattr(diag, "modified_by", ""),
                                }
                            )
        app.show_properties(meta=meta)

    def rename_selected_tree_item(self, app):
        item = app.analysis_tree.focus()
        tags = app.analysis_tree.item(item, "tags")
        if len(tags) != 2:
            return
        kind, ident = tags[0], tags[1]
        if SysMLRepository:
            repo = SysMLRepository.get_instance()
        else:  # pragma: no cover - fallback
            return
        current = ""
        node = None
        if kind in {"fmea", "fmeda", "hazop", "hara", "fi2tc", "tc2fi", "jrev"}:
            idx = int(ident)
            if kind == "fmea":
                current = app.fmeas[idx]["name"]
            elif kind == "fmeda":
                current = app.fmedas[idx]["name"]
            elif kind == "hazop":
                current = app.hazop_docs[idx].name
            elif kind == "hara":
                current = app.hara_docs[idx].name
            elif kind == "fi2tc":
                current = app.fi2tc_docs[idx].name
            elif kind == "tc2fi":
                current = app.tc2fi_docs[idx].name
            elif kind == "jrev":
                current = app.joint_reviews[idx].name
        elif kind == "gsn":
            diag = getattr(app, "gsn_diagram_map", {}).get(ident)
            if not diag:
                return
            current = diag.root.user_name
        elif kind == "gsnmod":
            module = getattr(app, "gsn_module_map", {}).get(ident)
            if not module:
                return
            current = module.name
        elif kind == "arch":
            diag = repo.diagrams.get(ident)
            current = diag.name if diag else ""
        elif kind == "gov":
            idx = int(ident)
            current = app.management_diagrams[idx].name
        elif kind == "fta":
            node = next((t for t in app.top_events if t.unique_id == int(ident)), None)
            current = node.user_name if node else ""
        elif kind == "pkg":
            pkg = repo.elements.get(ident)
            current = pkg.name if pkg else ""
        else:
            return
        new = simpledialog.askstring("Rename", "Enter new name:", initialvalue=current)
        if not new:
            return
        if kind == "fmea":
            old = app.fmeas[idx]["name"]
            app.fmeas[idx]["name"] = new
            app.safety_mgmt_toolbox.rename_document("FMEA", old, new)
        elif kind == "fmeda":
            doc = app.fmedas[idx]
            app.fmeda_manager.rename_fmeda(doc, new)
        elif kind == "hazop":
            old = app.hazop_docs[idx].name
            app.hazop_docs[idx].name = new
            app.safety_mgmt_toolbox.rename_document("HAZOP", old, new)
        elif kind == "hara":
            old = app.hara_docs[idx].name
            app.hara_docs[idx].name = new
            app.safety_mgmt_toolbox.rename_document("Risk Assessment", old, new)
        elif kind == "fi2tc":
            old = app.fi2tc_docs[idx].name
            app.fi2tc_docs[idx].name = new
            app.safety_mgmt_toolbox.rename_document("FI2TC", old, new)
        elif kind == "tc2fi":
            old = app.tc2fi_docs[idx].name
            app.tc2fi_docs[idx].name = new
            app.safety_mgmt_toolbox.rename_document("TC2FI", old, new)
        elif kind == "fta":
            node = next((t for t in app.top_events if t.unique_id == int(ident)), None)
            if node:
                old = node.user_name
                node.user_name = new
                analysis = (
                    "Prototype Assurance Analysis"
                    if getattr(app, "diagram_mode", "") == "PAA"
                    else "FTA"
                )
                app.safety_mgmt_toolbox.rename_document(analysis, old, new)
        elif kind == "arch" and repo.diagrams.get(ident):
            repo.diagrams[ident].name = new
        elif kind == "gov":
            app.management_diagrams[idx].name = new
        elif kind == "gsn":
            diag = app.gsn_diagram_map.get(ident)
            if diag:
                diag.root.user_name = new
        elif kind == "gsnmod":
            module = app.gsn_module_map.get(ident)
            if module:
                module.name = new
        elif kind == "jrev":
            if any(r.name == new for r in app.reviews if r is not app.joint_reviews[idx]):
                messagebox.showerror("Review", "Name already exists")
                return
            old = app.joint_reviews[idx].name
            app.joint_reviews[idx].name = new
            app.safety_mgmt_toolbox.rename_document("Joint Review", old, new)
        elif kind == "fta" and node:
            old = node.name
            node.user_name = new
            if hasattr(app, "safety_mgmt_toolbox"):
                analysis = (
                    "Prototype Assurance Analysis"
                    if getattr(app, "diagram_mode", "") == "PAA"
                    else "FTA"
                )
                app.safety_mgmt_toolbox.rename_document(analysis, old, node.name)
        elif kind == "pkg" and repo.elements.get(ident):
            repo.elements[ident].name = new
        app.update_views()
        if hasattr(app, "_arch_window") and app._arch_window.winfo_exists():
            app._arch_window.populate()
