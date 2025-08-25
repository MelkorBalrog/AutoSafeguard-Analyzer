"""UI setup helpers for AutoMLApp.

This module groups methods related to user interface
initialisation and diagram tab management. They are mixed into
:class:`~mainappsrc.core.automl_core.AutoMLApp` via
:class:`UISetupMixin` to keep ``automl_core`` lean.
"""

from __future__ import annotations

import tkinter as tk
from gui.utils.icon_factory import create_icon
from mainappsrc.managers.paa_manager import PrototypeAssuranceManager


class UISetupMixin:
    """Mixin providing UI setup and diagram management helpers."""

    def enable_fta_actions(self, enabled: bool) -> None:
        """Enable or disable FTA-related menu actions."""
        mode = getattr(self, "diagram_mode", "FTA")
        if hasattr(self, "fta_menu"):
            state = tk.NORMAL if enabled else tk.DISABLED
            for key in (
                "add_gate",
                "add_basic_event",
                "add_gate_from_failure_mode",
                "add_fault_event",
            ):
                self.fta_menu.entryconfig(self._fta_menu_indices[key], state=state)

    def enable_paa_actions(self, enabled: bool) -> None:
        """Enable or disable PAA-related menu actions."""
        if hasattr(self, "paa_menu"):
            state = tk.NORMAL if enabled else tk.DISABLED
            for key in ("add_confidence", "add_robustness"):
                self.paa_menu.entryconfig(self._paa_menu_indices[key], state=state)

    def _update_analysis_menus(self, mode: str | None = None) -> None:
        """Enable or disable node-adding menu items based on diagram mode."""
        if mode is None:
            mode = getattr(self, "diagram_mode", "FTA")
        self.enable_fta_actions(mode == "FTA")
        self.cta_manager.enable_actions(mode == "CTA")
        self.enable_paa_actions(mode == "PAA")

    def _create_paa_tab(self) -> None:
        """Delegate to :class:`PrototypeAssuranceManager` to create a PAA tab."""
        self.paa_manager._create_paa_tab()

    def create_paa_diagram(self) -> None:
        """Delegate to :class:`PrototypeAssuranceManager` for diagram setup."""
        self.paa_manager.create_paa_diagram()

    @property
    def paa_manager(self) -> PrototypeAssuranceManager:
        """Lazily create and return the PAA manager."""
        if not hasattr(self, "_paa_manager"):
            self._paa_manager = PrototypeAssuranceManager(self)
        return self._paa_manager

    def _reset_fta_state(self) -> None:
        """Clear references to the FTA tab and its canvas."""
        self.canvas_tab = None
        self.canvas_frame = None
        self.canvas = None
        self.hbar = None
        self.vbar = None
        self.page_diagram = None

    def ensure_fta_tab(self) -> None:
        """Recreate the FTA tab if it was closed."""
        mode = getattr(self, "diagram_mode", "FTA")
        tab_info = self.analysis_tabs.get(mode)
        if not tab_info or not tab_info["tab"].winfo_exists():
            self._create_fta_tab(mode)
        else:
            self.canvas_tab = tab_info["tab"]
            self.canvas = tab_info["canvas"]
            self.hbar = tab_info["hbar"]
            self.vbar = tab_info["vbar"]

    def _format_diag_title(self, diag) -> str:
        """Return SysML style title for a diagram tab."""
        if diag.name:
            return (
                f"\N{LEFT-POINTING DOUBLE ANGLE QUOTATION MARK}{diag.diag_type}"
                f"\N{RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK} {diag.name}"
            )
        return (
            f"\N{LEFT-POINTING DOUBLE ANGLE QUOTATION MARK}{diag.diag_type}"
            f"\N{RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK}"
        )

    def _create_icon(self, shape: str, color: str) -> tk.PhotoImage:
        """Delegate icon creation to the shared icon factory."""
        return create_icon(shape, color)

