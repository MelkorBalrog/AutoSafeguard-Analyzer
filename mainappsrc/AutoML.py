#!/usr/bin/env python3
# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file provides a thin interface wrapper around the full AutoML application
# implementation contained in :mod:`automl_core`.  All functionality remains in
# the external module so this wrapper exposes a simplified entry point while
# keeping the heavy implementation separated into sub-components.
"""Interface wrapper for the AutoML application."""

try:
    from .automl_core import (
        AutoMLApp as _AutoMLApp,
        AutoML_Helper,
        FaultTreeNode,
        GATE_NODE_TYPES,
        PMHF_TARGETS,
        VERSION,
        get_version,
        messagebox,
    )
except ImportError:  # pragma: no cover - fallback when executed as script
    import os
    import sys

    sys.path.append(os.path.dirname(__file__))
    from automl_core import (  # type: ignore
        AutoMLApp as _AutoMLApp,
        AutoML_Helper,
        FaultTreeNode,
        GATE_NODE_TYPES,
        PMHF_TARGETS,
        VERSION,
        get_version,
        messagebox,
    )

try:
    from .page_diagram import PageDiagram
except ImportError:  # pragma: no cover - script execution fallback
    import os
    import sys

    sys.path.append(os.path.dirname(__file__))
    from page_diagram import PageDiagram  # type: ignore

__all__ = [
    "AutoMLApp",
    "AutoML_Helper",
    "FaultTreeNode",
    "GATE_NODE_TYPES",
    "PMHF_TARGETS",
    "PageDiagram",
    "VERSION",
    "get_version",
    "messagebox",
]


class AutoMLApp:
    """Small delegating wrapper around the core :class:`AutoMLApp`.

    The goal of this class is to act purely as an interface layer. All
    functionality is implemented in :mod:`automl_core` and accessed through the
    ``_impl`` attribute. Any attribute or method not defined here is forwarded to
    the underlying implementation via ``__getattr__``.
    """

    def __init__(self, *args, **kwargs):
        self._impl = _AutoMLApp(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(self._impl, item)
