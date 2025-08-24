"""AutoML package exposing application classes lazily."""

from __future__ import annotations

import importlib
from types import ModuleType

_module: ModuleType | None = None


def __getattr__(name: str):
    global _module
    if _module is None:
        _module = importlib.import_module("mainappsrc.automl_core")
    return getattr(_module, name)


__all__: list[str] = []
