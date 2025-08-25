"""Custom control widgets for the AutoML GUI.

The messagebox module is imported lazily to avoid circular import issues.  It
depends on high level widgets defined in :mod:`gui.__init__`, so importing it
at module import time would cause a partially initialised package when
``gui`` itself loads controls.  ``__getattr__`` performs a deferred import when
``messagebox`` is first requested.
"""

from __future__ import annotations

from types import ModuleType
import importlib

from . import button_utils, mac_button_style

__all__ = ["button_utils", "mac_button_style", "messagebox"]


def __getattr__(name: str) -> ModuleType:
    """Dynamically import submodules on first access.

    Parameters
    ----------
    name:
        Attribute name being accessed.
    """

    if name == "messagebox":
        return importlib.import_module(f"{__name__}.messagebox")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
