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

from tkinter import simpledialog
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from gui.windows.architecture import InternalBlockDiagramWindow


class InternalBlockDiagramSubApp:
    """Create new internal block diagrams."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    def open(self) -> None:
        name = simpledialog.askstring(
            "New Internal Block Diagram", "Enter diagram name:"
        )
        if not name:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram(
            "Internal Block Diagram", name=name, package=repo.root_package.elem_id
        )
        tab = self.app._new_tab(self.app._format_diag_title(diag))
        self.app.diagram_tabs[diag.diag_id] = tab
        InternalBlockDiagramWindow(tab, self.app, diagram_id=diag.diag_id)
        self.app.refresh_all()

    # ------------------------------------------------------------------
    def create_export_window(self, parent, diagram):
        """Return a window instance for exporting *diagram*."""
        return InternalBlockDiagramWindow(parent, self.app, diagram_id=diagram.diag_id)
