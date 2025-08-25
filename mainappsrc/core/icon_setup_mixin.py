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
