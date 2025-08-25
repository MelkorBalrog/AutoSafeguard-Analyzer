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

"""CTA diagram utilities for AutoMLApp."""
from __future__ import annotations

import tkinter as tk
from typing import Dict


class ControlTreeManager:
    """Manage Control Tree Analysis (CTA) specific UI tasks."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app
        self.cta_menu: tk.Menu | None = None
        self._cta_menu_indices: Dict[str, int] = {}

    def register_menu(self, menu: tk.Menu, indices: Dict[str, int]) -> None:
        """Store CTA menu references for later manipulation."""
        self.cta_menu = menu
        self._cta_menu_indices = indices

    # ------------------------------------------------------------------
    def _create_tab(self) -> None:
        """Convenience wrapper for creating a CTA diagram tab."""
        self.app._create_fta_tab("CTA")

    def create_diagram(self) -> None:
        """Initialize a CTA diagram and its top-level event."""
        self._create_tab()
        self.app.add_top_level_event()
        if getattr(self.app, "cta_root_node", None):
            self.app.window_controllers.open_page_diagram(self.app.cta_root_node)

    def enable_actions(self, enabled: bool) -> None:
        """Enable or disable CTA-related menu actions."""
        if self.cta_menu is not None:
            state = tk.NORMAL if enabled else tk.DISABLED
            for key in ("add_trigger", "add_functional_insufficiency"):
                self.cta_menu.entryconfig(self._cta_menu_indices[key], state=state)
