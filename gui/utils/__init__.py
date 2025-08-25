"""Utility helpers re-exported for backwards compatibility."""

from . import logger as logger  # noqa: F401


def __getattr__(name: str):
    if name == "DIALOG_BG_COLOR":
        from .. import DIALOG_BG_COLOR  # Local import to avoid circular dependency
        return DIALOG_BG_COLOR
    raise AttributeError(name)


__all__ = ["logger", "DIALOG_BG_COLOR"]