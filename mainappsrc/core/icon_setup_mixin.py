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

"""Mix-in for building style-aware icons used across the UI."""

from gui.styles.style_manager import StyleManager


class IconSetupMixin:
    """Create and store commonly used icons."""

    def setup_icons(self) -> None:
        """Generate icons that adapt to the current theme."""
        style_mgr = StyleManager.get_instance()

        def _color(name: str, fallback: str = "black") -> str:
            color = style_mgr.get_color(name)
            return fallback if color == "#FFFFFF" else color

        self.pkg_icon = self._create_icon("folder", _color("Lifecycle Phase", "#b8860b"))
        self.gsn_module_icon = self.pkg_icon
        self.gsn_diagram_icon = self._create_icon("rect", "#4682b4")
        self.diagram_icons = {
            "Use Case Diagram": self._create_icon("usecase_diag", _color("Use Case Diagram", "blue")),
            "Activity Diagram": self._create_icon("activity_diag", _color("Activity Diagram", "green")),
            "Governance Diagram": self._create_icon("activity_diag", _color("Governance Diagram", "green")),
            "Block Diagram": self._create_icon("block_diag", _color("Block Diagram", "orange")),
            "Internal Block Diagram": self._create_icon("ibd_diag", _color("Internal Block Diagram", "purple")),
            "Control Flow Diagram": self._create_icon("activity_diag", _color("Control Flow Diagram", "red")),
        }
