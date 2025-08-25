"""Utility functions for GUI dialogs."""
from __future__ import annotations

from tkinter import simpledialog


def askstring_fixed(sd_module: simpledialog.__class__, title: str, prompt: str, **kwargs):
    """Display an ``askstring`` dialog with a fixed-size window.

    This helper temporarily patches the dialog class used by
    :func:`tkinter.simpledialog.askstring` so the resulting window cannot be
    resized.  The *sd_module* parameter should be the ``simpledialog`` module
    used by the caller so that test patches on that module remain effective.
    """
    original = sd_module._QueryString

    class FixedQueryString(sd_module._QueryString):  # type: ignore[attr-defined]
        """Query dialog variant that disables window resizing."""

        def body(self, master):  # type: ignore[override]
            self.resizable(False, False)
            return super().body(master)

    sd_module._QueryString = FixedQueryString  # type: ignore[attr-defined]
    try:
        return sd_module.askstring(title, prompt, **kwargs)
    finally:
        sd_module._QueryString = original  # type: ignore[attr-defined]
