"""Prototype Assurance Analysis utilities for AutoMLApp."""
from __future__ import annotations

import tkinter as tk


class PrototypeAssuranceManager:
    """Encapsulate Prototype Assurance Analysis operations."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    def enable_paa_actions(self, enabled: bool) -> None:
        """Enable or disable PAA-related menu actions."""
        if hasattr(self.app, "paa_menu"):
            state = tk.NORMAL if enabled else tk.DISABLED
            for key in ("add_confidence", "add_robustness"):
                self.app.paa_menu.entryconfig(
                    self.app._paa_menu_indices[key], state=state
                )

    def _create_paa_tab(self) -> None:
        """Convenience wrapper for creating a PAA diagram."""
        self.app._create_fta_tab("PAA")

    def create_paa_diagram(self) -> None:
        """Initialize a Prototype Assurance Analysis diagram and its top-level event."""
        self._create_paa_tab()
        self.app.add_top_level_event()
        if getattr(self.app, "paa_root_node", None):
            self.app.open_page_diagram(self.app.paa_root_node)
