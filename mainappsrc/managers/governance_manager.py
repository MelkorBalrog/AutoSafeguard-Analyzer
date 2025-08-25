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

"""Governance management helpers for :class:`AutoMLApp`.

This module centralises interactions with the Safety Management Toolbox so the
main application can delegate governance specific operations.  The manager
controls lifecycle module activation, toolbox change propagation and diagram
freezing utilities.
"""


from typing import Optional, Iterable
import tkinter as tk


class GovernanceManager:
    """Coordinate governance related features for the application.

    Parameters
    ----------
    app:
        The :class:`AutoMLApp` instance using this manager.  The manager calls
        back into the application to enable/disable tools and to refresh views.
    """

    def __init__(self, app: "AutoMLApp") -> None:  # pragma: no cover - simple init
        self.app = app
        self.toolbox = None

    # ------------------------------------------------------------------
    def attach_toolbox(self, toolbox) -> None:
        """Register the toolbox and hook change notifications."""
        self.toolbox = toolbox
        if self.toolbox is not None:
            self.toolbox.on_change = self._on_toolbox_change

    # ------------------------------------------------------------------
    def freeze_governance_diagrams(self, freeze: bool) -> None:
        """Freeze or unfreeze all registered governance diagrams."""
        if self.toolbox is not None:
            self.toolbox.set_all_diagrams_frozen(freeze)

    # ------------------------------------------------------------------
    def set_active_module(self, module: Optional[str]) -> None:
        """Activate the requested lifecycle module in the toolbox."""
        if self.toolbox is not None:
            self.toolbox.set_active_module(module)
        var = getattr(self.app, "lifecycle_var", None)
        if var is not None and hasattr(var, "set"):
            var.set(module or "")

    # ------------------------------------------------------------------
    def update_lifecycle_cb(self) -> None:
        """Refresh the lifecycle combobox with available modules."""
        cb = getattr(self.app, "lifecycle_cb", None)
        if cb is None:
            return
        smt = self.toolbox
        list_modules = getattr(smt, "list_modules", None)
        names: Iterable[str]
        if callable(list_modules):
            names = list_modules()
        else:
            names = [m.name for m in getattr(smt, "modules", [])]
        cb.configure(values=names)
        active = getattr(smt, "active_module", None)
        var = getattr(self.app, "lifecycle_var", None)
        if var is not None and hasattr(var, "set"):
            if active in names:
                var.set(active)
            else:
                var.set("")

    # ------------------------------------------------------------------
    def apply_governance_rules(self) -> None:
        """Public entry point used by the application to refresh tools."""
        try:
            self._on_toolbox_change()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def on_lifecycle_selected(self, phase: Optional[str]) -> None:
        """Handle lifecycle combobox changes.

        Parameters
        ----------
        phase:
            Name of the newly selected lifecycle phase. ``None`` clears any
            active module selection.
        """

        if hasattr(self.app, "active_phase_lbl"):
            self.app.active_phase_lbl.config(
                text=f"Active phase: {phase or 'None'}"
            )
        self.set_active_module(phase or None)
        try:
            if hasattr(self.app, "update_views"):
                self.app.update_views()
        except Exception:
            pass
        try:
            self.refresh_tool_enablement()
        except Exception:
            pass
        for name in (
            "_hazop_window",
            "_risk_window",
            "_stpa_window",
            "_threat_window",
            "_fi2tc_window",
            "_tc2fi_window",
        ):
            win = getattr(self.app, name, None)
            if win and getattr(win, "refresh_docs", None) and getattr(
                win, "winfo_exists", lambda: False
            )():
                win.refresh_docs()

        def _refresh_children(widget):
            if hasattr(widget, "refresh_from_repository"):
                widget.refresh_from_repository()
            for ch in getattr(widget, "winfo_children", lambda: [])():
                _refresh_children(ch)

        for tab in getattr(self.app, "diagram_tabs", {}).values():
            _refresh_children(tab)

    # ------------------------------------------------------------------
    def create_export_window(self, parent, diagram):
        """Return a GovernanceDiagramWindow for *diagram*."""
        from gui.architecture import GovernanceDiagramWindow

        return GovernanceDiagramWindow(parent, self.app, diagram_id=diagram.diag_id)

    # ------------------------------------------------------------------
    def _on_toolbox_change(self) -> None:
        """Handle toolbox modifications."""
        self.refresh_tool_enablement()
        refresh_menu = getattr(self.app, "_refresh_phase_requirements_menu", None)
        if refresh_menu:
            refresh_menu()
        try:
            if hasattr(self.app, "update_views"):
                self.app.update_views()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def refresh_tool_enablement(self) -> None:
        """Enable or disable tools based on toolbox configuration."""
        if not hasattr(self.app, "tool_listboxes"):
            return
        toolbox = self.toolbox
        if toolbox:
            declared = set(toolbox.enabled_products())
            for name in list(declared):
                parent = self.app.WORK_PRODUCT_PARENTS.get(name)
                while parent:
                    declared.add(parent)
                    parent = self.app.WORK_PRODUCT_PARENTS.get(parent)
            current = set(getattr(self.app, "enabled_work_products", set()))
            for name in declared - current:
                try:
                    self.app.enable_work_product(name)
                except Exception:
                    self.app.enabled_work_products.add(name)
            if getattr(toolbox, "work_products", None) or toolbox.active_module:
                for name in current - declared:
                    try:
                        self.app.disable_work_product(name, force=True)
                    except Exception:
                        pass
        global_enabled = getattr(self.app, "enabled_work_products", set())
        if toolbox and (getattr(toolbox, "work_products", None) or toolbox.active_module):
            phase_enabled = toolbox.enabled_products()
            for name in list(phase_enabled):
                parent = self.app.WORK_PRODUCT_PARENTS.get(name)
                while parent:
                    phase_enabled.add(parent)
                    parent = self.app.WORK_PRODUCT_PARENTS.get(parent)
        else:
            phase_enabled = global_enabled
        enabled = global_enabled & phase_enabled
        for lb in self.app.tool_listboxes.values():
            for i, tool_name in enumerate(lb.get(0, tk.END)):
                analysis_names = getattr(self.app, "tool_to_work_product", {}).get(tool_name, set())
                if isinstance(analysis_names, str):
                    analysis_names = {analysis_names}
                if not analysis_names:
                    in_enabled = tool_name in enabled
                else:
                    in_enabled = any(n in enabled for n in analysis_names)
                lb.itemconfig(i, foreground="gray" if not in_enabled else "black")
        entry_state: dict[tuple[tk.Menu, int], bool] = {}
        for wp, menus in getattr(self.app, "work_product_menus", {}).items():
            is_enabled = wp in enabled
            for menu, idx in menus:
                key = (menu, idx)
                entry_state[key] = entry_state.get(key, False) or is_enabled
        for (menu, idx), is_enabled in entry_state.items():
            try:
                menu.entryconfig(idx, state=tk.NORMAL if is_enabled else tk.DISABLED)
            except tk.TclError:
                pass
