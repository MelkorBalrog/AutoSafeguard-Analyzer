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

"""Helpers for fault tree top event workflows.

The :class:`Top_Event_Workflows` class centralises operations related to
creating and manipulating top events within a fault tree.  It is
instantiated by :class:`AutoMLApp` and delegates to existing FTA
utilities when required.
"""

from gui.controls import messagebox

from ..models.fta.fault_tree_node import FaultTreeNode


class Top_Event_Workflows:
    """Provide helpers for top event manipulation."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # ------------------------------------------------------------------
    # Helpers for malfunctions and failure modes
    def create_top_event_for_malfunction(self, name: str) -> None:
        """Create a new top level event linked to the given malfunction."""
        app = self.app
        app.push_undo_state()
        new_event = FaultTreeNode("", "TOP EVENT")
        new_event.x, new_event.y = 300, 200
        new_event.is_top_event = True
        new_event.malfunction = name
        app.top_events.append(new_event)
        app.root_node = new_event
        if hasattr(app, "safety_mgmt_toolbox"):
            analysis = (
                "Prototype Assurance Analysis"
                if getattr(app, "diagram_mode", "") == "PAA"
                else "FTA"
            )
            app.safety_mgmt_toolbox.register_created_work_product(
                analysis, new_event.name
            )
        app.update_views()

    def add_gate_from_failure_mode(self) -> None:
        app = self.app
        app.push_undo_state()
        modes = app.get_available_failure_modes_for_gates()
        if not modes:
            messagebox.showinfo("No Failure Modes", "No failure modes available.")
            return
        dialog = app.SelectFailureModeDialog(app.root, app, modes)
        selected = dialog.selected
        if not selected:
            return
        if app.selected_node:
            parent_node = app.selected_node
            if not parent_node.is_primary_instance:
                messagebox.showwarning(
                    "Invalid Operation",
                    "Cannot add to a clone node. Select the original.",
                )
                return
        else:
            sel = app.analysis_tree.selection()
            if not sel:
                messagebox.showwarning(
                    "No selection", "Select a parent node to paste into."
                )
                return
            try:
                node_id = int(app.analysis_tree.item(sel[0], "tags")[0])
            except (IndexError, ValueError):
                messagebox.showwarning(
                    "No selection", "Select a parent node from the tree."
                )
                return
            parent_node = app.find_node_by_id_all(node_id)
        if parent_node.node_type.upper() in [
            "CONFIDENCE LEVEL",
            "ROBUSTNESS SCORE",
            "BASIC EVENT",
        ]:
            messagebox.showwarning("Invalid", "Base events cannot have children.")
            return
        new_node = FaultTreeNode("", "GATE", parent=parent_node)
        new_node.gate_type = "AND"
        if hasattr(selected, "unique_id"):
            new_node.failure_mode_ref = selected.unique_id
            new_node.description = getattr(selected, "description", "")
            new_node.user_name = getattr(selected, "user_name", "")
        else:
            new_node.description = app.get_entry_field(selected, "description", "")
            new_node.user_name = app.get_entry_field(selected, "user_name", "")
        new_node.x = parent_node.x + 100
        new_node.y = parent_node.y + 100
        parent_node.children.append(new_node)
        new_node.parents.append(parent_node)
        app.update_views()

    def get_top_event(self, node):
        return self.app.fta_app.get_top_event(self.app, node)

    def generate_top_event_summary(self, top_event):
        return self.app.fta_app.generate_top_event_summary(self.app, top_event)

