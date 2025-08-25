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

"""User management utilities for AutoMLApp."""

from tkinter import simpledialog
from gui.toolboxes.review_toolbox import UserSelectDialog as ReviewUserSelectDialog


class UserManager:
    """Handle user interactions and roles for :class:`AutoMLApp`."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # --- User editing -------------------------------------------------
    def edit_user_name(self) -> None:
        """Edit the user name of the currently selected node."""
        app = self.app
        node = app.selected_node
        mb = app.messagebox
        if node:
            if getattr(node, "name_readonly", False):
                mb.showinfo("Product Goal", "Edit via Product Goal editor")
                return
            new_name = simpledialog.askstring(
                "Edit User Name", "Enter new user name:", initialvalue=node.user_name
            )
            if new_name is not None:
                node.user_name = new_name.strip()
                app.sync_nodes_by_id(node)
                app.update_views()
        else:
            mb.showwarning("Edit User Name", "Select a node first.")

    # --- Review helpers -----------------------------------------------
    def set_current_user(self) -> None:
        """Prompt for a user and set it as the current reviewer."""
        app = self.app
        mb = app.messagebox
        if not app.review_data:
            mb.showwarning("User", "Start a review first")
            return
        parts = app.review_data.participants + app.review_data.moderators
        dlg = ReviewUserSelectDialog(app.root, parts, initial_name=app.current_user)
        if not dlg.result:
            return
        name, _ = dlg.result
        allowed = [p.name for p in parts]
        if name not in allowed:
            mb.showerror("User", "Name not found in participants")
            return
        app.current_user = name

    def get_current_user_role(self):
        """Return the role of the currently selected review user."""
        app = self.app
        if not app.review_data:
            return None
        if app.current_user in [m.name for m in app.review_data.moderators]:
            return "moderator"
        for participant in app.review_data.participants:
            if participant.name == app.current_user:
                return participant.role
        return None
