"""User management utilities for AutoMLApp."""
from __future__ import annotations

from tkinter import simpledialog
from gui.review_toolbox import UserSelectDialog as ReviewUserSelectDialog


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
