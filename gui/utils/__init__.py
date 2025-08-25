"""Utility helpers exposed for backward-compatible imports.

This package re-exports commonly used utilities so that modules can simply
``import gui.utils`` and access members such as :mod:`logger` or
``DIALOG_BG_COLOR``.  Keeping these aliases here preserves compatibility with
older code that expected these objects to live directly under
``gui.utils``.
"""

# The logging helper is implemented in ``logger.py`` but we import it here so
# ``from gui.utils import logger`` continues to work.
from . import logger  # noqa: F401


# Default background colour used by dialog windows across the application.
# This constant is defined here to allow both ``from gui.utils import
# DIALOG_BG_COLOR`` and ``from gui import DIALOG_BG_COLOR`` (which imports it
# via ``gui.__init__``).
DIALOG_BG_COLOR = "#A9BCE2"


__all__ = ["logger", "DIALOG_BG_COLOR"]
