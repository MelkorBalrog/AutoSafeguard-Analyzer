from __future__ import annotations

"""Mix-in providing GUI style configuration for :class:`AutoMLApp`."""

from tkinter import ttk

from mainappsrc.subapps.style_subapp import StyleSubApp


class StyleSetupMixin:
    """Configure application styles and themed assets."""

    def setup_style(self, root) -> None:
        """Initialise ttk style and apply the user's theme.

        Parameters
        ----------
        root:
            The Tk root window used by the application.
        """
        self.style = ttk.Style()
        self.style_app = StyleSubApp(root, self.style)
        self.style_app.apply()
        self._btn_imgs = self.style_app.btn_images
        if hasattr(self, "lifecycle_ui"):
            self.lifecycle_ui._init_nav_button_style()
