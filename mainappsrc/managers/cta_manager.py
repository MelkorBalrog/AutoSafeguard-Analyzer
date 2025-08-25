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
