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

"""Utility class to handle GSN specific UI actions."""

import tkinter as tk
from typing import TYPE_CHECKING, Optional

from gui.explorers.gsn_explorer import GSNExplorer
from gui.windows.gsn_diagram_window import GSNDiagramWindow, GSN_WINDOWS

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .AutoML import AutoMLApp


class GSNManager:
    """Manage GSN explorers and diagram windows.

    The manager centralises creation and refreshing of GSN related views so the
    main :class:`AutoMLApp` can delegate these responsibilities.
    """

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app
        self._gsn_tab: Optional[tk.Widget] = None
        self._gsn_window: Optional[GSNExplorer] = None

    # ------------------------------------------------------------------
    def manage_gsn(self) -> None:  # pragma: no cover - requires tkinter
        """Show the GSN explorer tab, creating it if necessary."""
        if self._gsn_tab and self._gsn_tab.winfo_exists():
            self.app.doc_nb.select(self._gsn_tab)
        else:
            self._gsn_tab = self.app._new_tab("GSN Explorer")
            self._gsn_window = GSNExplorer(self._gsn_tab, self.app)
            self._gsn_window.pack(fill=tk.BOTH, expand=True)
        self.app.refresh_all()

    # ------------------------------------------------------------------
    def open_diagram(self, diagram) -> None:  # pragma: no cover - requires tkinter
        """Open *diagram* inside a new notebook tab."""
        existing = self.app.diagram_tabs.get(diagram.diag_id)
        if existing and str(existing) in self.app.doc_nb.tabs():
            if existing.winfo_exists():
                self.app.doc_nb.select(existing)
                self.app.refresh_all()
                return
            self.app.diagram_tabs.pop(diagram.diag_id, None)
        tab = self.app._new_tab(diagram.root.user_name)
        self.app.diagram_tabs[diagram.diag_id] = tab
        window = GSNDiagramWindow(tab, self.app, diagram)
        setattr(tab, "gsn_window", window)
        self.app.refresh_all()

    # ------------------------------------------------------------------
    def refresh(self) -> None:  # pragma: no cover - requires tkinter
        """Refresh open GSN windows."""
        if self._gsn_window and self._gsn_window.winfo_exists():
            if hasattr(self._gsn_window, "refresh"):
                self._gsn_window.refresh()
        for ref in list(GSN_WINDOWS):
            win = ref()
            if win and hasattr(win, "winfo_exists") and win.winfo_exists():
                if hasattr(win, "refresh_from_repository"):
                    win.refresh_from_repository()
                elif hasattr(win, "refresh"):
                    win.refresh()
