"""Clipboard strategies for SysML diagram operations.

This module provides multiple implementations for storing and
retrieving diagram objects when copying, cutting and pasting.
Each strategy offers a different mechanism.  The default strategy is
:class:`ClassClipboardStrategy`, which keeps the clipboard at the class
level and allows sharing between diagram instances of the same type.
"""

from __future__ import annotations

from dataclasses import dataclass
import copy
import pickle
from typing import Any, Protocol

try:
    import tkinter as tk
except Exception:  # pragma: no cover - environments without Tk
    tk = None  # type: ignore


class ClipboardStrategy(Protocol):
    """Protocol for clipboard behaviour."""

    def copy(self, obj: Any) -> None:
        """Store ``obj`` in the clipboard."""

    def paste(self) -> Any:
        """Return a deep copy of the clipboard contents."""


@dataclass
class ModuleClipboardStrategy:
    """Simple module level clipboard using a global variable."""

    _clipboard: Any | None = None

    def copy(self, obj: Any) -> None:  # pragma: no cover - trivial
        self._clipboard = copy.deepcopy(obj)

    def paste(self) -> Any:  # pragma: no cover - trivial
        return copy.deepcopy(self._clipboard)


@dataclass
class ClassClipboardStrategy:
    """Clipboard stored on the strategy class itself."""

    _clipboard: Any | None = None

    def copy(self, obj: Any) -> None:
        type(self)._clipboard = copy.deepcopy(obj)

    def paste(self) -> Any:
        return copy.deepcopy(type(self)._clipboard)


@dataclass
class TkClipboardStrategy:
    """Clipboard using the Tk root clipboard with pickle serialisation."""

    root: tk.Misc

    def copy(self, obj: Any) -> None:
        data = pickle.dumps(obj)
        self.root.clipboard_clear()
        self.root.clipboard_append(data.decode("latin1"))

    def paste(self) -> Any:
        try:
            data = self.root.clipboard_get().encode("latin1")
            return pickle.loads(data)
        except Exception:  # pragma: no cover - clipboard unavailable
            return None


@dataclass
class RepositoryClipboardStrategy:
    """Clipboard stored on a repository-like object."""

    repo: Any

    def copy(self, obj: Any) -> None:
        self.repo._clipboard = copy.deepcopy(obj)

    def paste(self) -> Any:
        return copy.deepcopy(getattr(self.repo, "_clipboard", None))


# Expose all strategies for testing, default to class-level
DEFAULT_STRATEGY = ClassClipboardStrategy()
